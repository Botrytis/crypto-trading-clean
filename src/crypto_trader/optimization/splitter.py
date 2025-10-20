"""
Data Splitting for Walk-Forward Optimization

Splits time-series data into Train/Validation/Test sets.
Prevents lookahead bias and ensures temporal ordering.
"""

from datetime import datetime, timedelta
from typing import Tuple, List
import pandas as pd
from loguru import logger


class DataSplitter:
    """
    Time-series aware data splitter for backtesting.

    Ensures no data leakage by maintaining temporal order.
    """

    def __init__(
        self,
        train_pct: float = 0.6,
        val_pct: float = 0.2,
        test_pct: float = 0.2
    ):
        """
        Initialize splitter with split percentages.

        Args:
            train_pct: Percentage for training (0.0-1.0)
            val_pct: Percentage for validation (0.0-1.0)
            test_pct: Percentage for testing (0.0-1.0)
        """
        if not abs(train_pct + val_pct + test_pct - 1.0) < 0.001:
            raise ValueError("Split percentages must sum to 1.0")

        self.train_pct = train_pct
        self.val_pct = val_pct
        self.test_pct = test_pct

        logger.info(f"DataSplitter initialized: {train_pct:.0%} train, {val_pct:.0%} val, {test_pct:.0%} test")

    def split(
        self,
        data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically into train/val/test sets.

        Args:
            data: DataFrame with datetime index or timestamp column

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if data.empty:
            raise ValueError("Cannot split empty dataframe")

        # Ensure data has timestamp
        df = data.copy()
        if 'timestamp' not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("Data must have 'timestamp' column or DatetimeIndex")

        # Sort by time
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.sort_index()
            timestamps = df.index
        else:
            df = df.sort_values('timestamp')
            timestamps = pd.to_datetime(df['timestamp'])

        n = len(df)
        train_end = int(n * self.train_pct)
        val_end = int(n * (self.train_pct + self.val_pct))

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()

        logger.info(f"Split data: {len(train_df)} train, {len(val_df)} val, {len(test_df)} test")
        logger.info(f"  Train: {timestamps.iloc[0]} to {timestamps.iloc[train_end-1]}")
        logger.info(f"  Val:   {timestamps.iloc[train_end]} to {timestamps.iloc[val_end-1]}")
        logger.info(f"  Test:  {timestamps.iloc[val_end]} to {timestamps.iloc[-1]}")

        return train_df, val_df, test_df

    def walk_forward_splits(
        self,
        data: pd.DataFrame,
        n_splits: int = 5,
        test_size_pct: float = 0.2
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Create multiple walk-forward train/test splits.

        Each split uses all previous data for training and next period for testing.
        This simulates real trading conditions where you optimize on past data
        and test on unseen future data.

        Args:
            data: Full dataset
            n_splits: Number of walk-forward iterations
            test_size_pct: Size of test set as percentage of data

        Returns:
            List of (train_df, test_df) tuples
        """
        if data.empty:
            raise ValueError("Cannot split empty dataframe")

        df = data.copy()
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.sort_index()
        else:
            df = df.sort_values('timestamp')

        n = len(df)
        test_size = int(n * test_size_pct)
        min_train = int(n * 0.3)  # Minimum 30% for initial training

        if test_size < 10:
            raise ValueError(f"Test size too small: {test_size} rows")

        if min_train + test_size * n_splits > n:
            raise ValueError(f"Not enough data for {n_splits} splits")

        splits = []

        for i in range(n_splits):
            train_end = min_train + (test_size * i)
            test_end = train_end + test_size

            if test_end > n:
                break

            train_df = df.iloc[:train_end].copy()
            test_df = df.iloc[train_end:test_end].copy()

            splits.append((train_df, test_df))

            logger.debug(f"Split {i+1}: {len(train_df)} train, {len(test_df)} test")

        logger.info(f"Created {len(splits)} walk-forward splits")
        return splits
