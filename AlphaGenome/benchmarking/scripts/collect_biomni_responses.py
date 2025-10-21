#!/usr/bin/env python
"""
Biomni Agent Response Collection Script

This script loads a benchmark CSV dataset and runs each query through the Biomni A1 agent
to collect agent responses. It updates the CSV with the agent responses for further analysis.

The Biomni agent provides responses as tuples where:
- First element: Full response text
- Second element: Final results text
"""

import os
import sys
import argparse
import time
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging

# Import Biomni agent
from biomni.agent import A1

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('biomni_response_collection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_benchmark_csv(csv_path: str) -> pd.DataFrame:
    """
    Load the benchmark CSV file and validate its structure.
    
    Args:
        csv_path: Path to the benchmark CSV file
        
    Returns:
        pandas DataFrame with the benchmark data
    """
    try:
        df = pd.read_csv(csv_path)
        required_columns = ['repo', 'path', 'type', 'question', 'answer', 'run_date', 'agent_response', 'grade', 'grade_comments']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.info(f"Loaded benchmark CSV with {len(df)} questions")
        return df
        
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_path}: {e}")
        raise


def create_biomni_prompt(question: str, context: Optional[str] = None) -> str:
    """
    Create a prompt for the Biomni A1 agent.
    
    Args:
        question: The question to ask
        context: Optional context about the question
        
    Returns:
        Formatted prompt string
    """
    base_prompt = f"""Use AlphaGenome (https://github.com/google-deepmind/alphagenome) to answer the following question. You can find the ALPHAGENOME_API_KEY in the .env file for this project.

Question: {question}

IMPORTANT: You final response must be a valid JSON object containing exactly two fields:
1. "final_answer": A concise answer containing just the requested value (e.g., a number, gene name, or specific result)
2. "reasoning": Your step-by-step reasoning and any calculations you performed

Example response format:
{{
  "final_answer": "GENE_NAME",
  "reasoning": "I used the AlphaGenome variant scoring tool to analyze the variant chr1:1234567:A>C for RNA-seq predictions in Colon - Transverse tissue. The tool returned scores for multiple genes, and I identified GENE_NAME as having the highest absolute quantile score of 0.987."
}}

Please ensure your response is valid JSON and the final_answer field contains only the requested value. Do NOT provide any other text or formatting."""

    if context:
        base_prompt = f"Context: {context}\n\n{base_prompt}"
    
    return base_prompt


def run_biomni_agent(prompt: str, agent: A1, max_retries: int = 2, timeout: int = 600) -> tuple[Optional[str], Optional[str], Optional[dict], Optional[float], float]:
    """
    Run the Biomni A1 agent with the given prompt and return (response_text, full_response_text, usage_dict, total_cost_usd, runtime_seconds).
    
    Args:
        prompt: The prompt to send to the agent
        agent: The Biomni A1 agent instance
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for each attempt
        
    Returns:
        Tuple containing (response_text, full_response_text, usage_dict, total_cost_usd, runtime_seconds)
        Note: Biomni may not provide usage info, so usage_dict and total_cost_usd may be None
    """
    for attempt in range(max_retries):
        start_time = time.time()
        try:
            logger.info(f"Running Biomni A1 agent (attempt {attempt + 1}/{max_retries})")
            
            # Run the agent with timeout
            response_tuple = agent.go(prompt)
            duration = time.time() - start_time
            
            if response_tuple and len(response_tuple) >= 2:
                # Extract response components
                full_response_text = response_tuple[0]  # Full response
                final_results_text = response_tuple[1]  # Final results
                
                logger.info("Successfully got response from Biomni A1 agent")
                
                # Biomni doesn't provide usage info, so return None for usage and cost
                return final_results_text, full_response_text, None, None, duration
            else:
                logger.warning(f"Unexpected response format from Biomni agent: {response_tuple}")
                
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"Error running Biomni A1 agent (attempt {attempt + 1}): {e}")
        
        # Wait before retry
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    logger.error("Failed to get response from Biomni A1 agent after all retries")
    return None, None, None, None, 0.0


def process_question(row: pd.Series, question_index: int, total_questions: int, agent: A1, timeout: int = 600, max_retries: int = 2, force_rerun: bool = False) -> Dict[str, Any]:
    """
    Process a single question and get the agent response.
    
    Args:
        row: DataFrame row containing question data
        question_index: Index of the current question (0-based)
        total_questions: Total number of questions
        agent: The Biomni A1 agent instance
        timeout: Timeout in seconds for agent calls
        max_retries: Maximum number of retry attempts for agent calls
        force_rerun: If True, rerun questions that already have responses; if False, skip them
        
    Returns:
        Dictionary with updated row data
    """
    logger.info(f"Processing question {question_index + 1}/{total_questions}: {row['question'][:100]}...")
    
    # Skip if we already have an agent response (unless force_rerun is True)
    if pd.notna(row['agent_response']) and row['agent_response'].strip() and not force_rerun:
        logger.info(f"Question {question_index + 1} already has agent response, skipping (use --force-rerun to override)")
        return row.to_dict()
    elif pd.notna(row['agent_response']) and row['agent_response'].strip() and force_rerun:
        logger.info(f"Question {question_index + 1} already has agent response, but force_rerun is enabled - will rerun")
    
    # Create the prompt
    prompt = create_biomni_prompt(row['question'])
    
    # Get response from Biomni A1 agent
    agent_response, full_response_text, usage, total_cost_usd, runtime_sec = run_biomni_agent(prompt, agent, max_retries=max_retries, timeout=timeout)
    
    # Update the row data
    updated_row = row.to_dict()
    if agent_response:
        updated_row['agent_response'] = agent_response
        logger.info(f"Successfully collected response for question {question_index + 1}")
    else:
        updated_row['agent_response'] = "ERROR: Failed to get response from Biomni A1 agent"
        logger.error(f"Failed to get response for question {question_index + 1}")

    # Record runtime (seconds)
    updated_row['run_time_seconds'] = round(runtime_sec, 3)

    # Biomni doesn't provide token usage info, so set these to None
    updated_row['tokens_input'] = None
    updated_row['tokens_output'] = None
    updated_row['cache_creation_input_tokens'] = None
    updated_row['cache_read_input_tokens'] = None
    updated_row['total_tokens'] = None
    updated_row['num_turns'] = None
    updated_row['total_cost_usd'] = None
    
    return updated_row


def save_updated_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the updated DataFrame to CSV.
    
    Args:
        df: Updated DataFrame
        output_path: Path to save the updated CSV
    """
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Updated CSV saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving updated CSV: {e}")
        raise


def main():
    """Main function to run the Biomni agent response collection script."""
    parser = argparse.ArgumentParser(
        description='Collect agent responses for benchmark questions using Biomni A1 agent'
    )
    parser.add_argument(
        'input_csv',
        help='Path to the benchmark CSV file (e.g., ag_tutorial_benchmark_2025-09-25.csv)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output CSV file path (default: input file with _with_biomni_responses suffix)'
    )
    parser.add_argument(
        '--start-index', '-s',
        type=int,
        default=0,
        help='Index to start processing from (default: 0)'
    )
    parser.add_argument(
        '--end-index', '-e',
        type=int,
        help='Index to end processing at (default: process all remaining questions)'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        default=2,
        help='Maximum number of retries for agent calls (default: 2)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Timeout in seconds for agent calls (default: 600)'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default='~/projects/Biomni/data',
        help='Path to Biomni data directory (default: ~/projects/Biomni/data)'
    )
    parser.add_argument(
        '--llm',
        type=str,
        default='claude-sonnet-4-20250514',
        help='LLM model to use (default: claude-sonnet-4-20250514)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--force-rerun', '-f',
        action='store_true',
        help='Force rerun of questions that already have agent responses (default: skip existing responses)'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input file
    if not os.path.exists(args.input_csv):
        logger.error(f"Input CSV file not found: {args.input_csv}")
        sys.exit(1)
    
    # Set output path
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input_csv)
        output_path = input_path.parent / f"{input_path.stem}_with_biomni_responses{input_path.suffix}"
    
    try:
        # Initialize Biomni A1 agent
        logger.info(f"Initializing Biomni A1 agent with data path: {args.data_path}")
        logger.info(f"Using LLM model: {args.llm}")
        agent = A1(path=args.data_path, llm=args.llm)
        
        # Load the benchmark CSV
        df = load_benchmark_csv(args.input_csv)
        
        # Determine processing range
        start_idx = args.start_index
        end_idx = args.end_index if args.end_index is not None else len(df)
        
        if start_idx < 0 or start_idx >= len(df):
            logger.error(f"Start index {start_idx} is out of range (0-{len(df)-1})")
            sys.exit(1)
        
        if end_idx > len(df):
            logger.warning(f"End index {end_idx} exceeds data length {len(df)}, using {len(df)}")
            end_idx = len(df)
        
        logger.info(f"Processing questions {start_idx} to {end_idx-1} ({end_idx-start_idx} questions)")
        
        # Process each question in the specified range
        updated_rows = []
        for i in range(start_idx, end_idx):
            row = df.iloc[i]
            updated_row = process_question(row, i, len(df), agent, args.timeout, args.max_retries, args.force_rerun)
            updated_rows.append(updated_row)
            
            # Save progress every 5 questions
            if (i - start_idx + 1) % 5 == 0:
                temp_df = pd.DataFrame(updated_rows)
                temp_output = f"{output_path}.temp"
                temp_df.to_csv(temp_output, index=False)
                logger.info(f"Progress saved to {temp_output}")
        
        # Create updated DataFrame with all columns for the processed range
        updated_df = pd.DataFrame(updated_rows)
        
        # Reconstruct the full DataFrame preserving all existing data
        # First, ensure all new columns exist in the original DataFrame
        for col in updated_df.columns:
            if col not in df.columns:
                df[col] = None  # Initialize with None/NaN
        
        # Update only the processed rows, preserving all other rows as-is
        df.iloc[start_idx:end_idx] = updated_df
        final_df = df
        
        # Save the final result
        save_updated_csv(final_df, output_path)
        
        # Clean up temporary file
        temp_file = f"{output_path}.temp"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info("Cleaned up temporary file")
        
        logger.info(f"Successfully processed {end_idx-start_idx} questions")
        logger.info(f"Results saved to: {output_path}")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()