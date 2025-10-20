"""
Strategies API Routes

Endpoints for listing, retrieving, and managing trading strategies.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from crypto_trader.strategies import get_registry

router = APIRouter()


class StrategyInfo(BaseModel):
    """Strategy information model."""
    name: str
    description: str
    parameters: Dict[str, Any]
    tags: List[str] = []
    complexity: str = "medium"
    recommended_timeframes: List[str] = []


class StrategyListResponse(BaseModel):
    """Response model for strategy list."""
    total: int
    strategies: List[StrategyInfo]


@router.get("/", response_model=StrategyListResponse)
async def list_strategies(
    tag: str = None,
    complexity: str = None,
) -> StrategyListResponse:
    """
    List all available trading strategies.

    Query Parameters:
        tag: Filter by strategy tag (trend-following, mean-reversion, etc.)
        complexity: Filter by complexity (low, medium, high)

    Returns:
        List of strategy information
    """
    try:
        registry = get_registry()
        all_strategies = []

        for strategy_name, strategy_class in registry.items():
            # Create temporary instance to get info
            try:
                strategy = strategy_class()

                # Get parameters (with defaults if available)
                try:
                    params = strategy.get_parameters() if hasattr(strategy, 'get_parameters') else {}
                except:
                    params = {}

                # Build strategy info
                strategy_info = StrategyInfo(
                    name=strategy_name,
                    description=strategy.__class__.__doc__ or f"{strategy_name} trading strategy",
                    parameters=params,
                    tags=getattr(strategy, 'tags', []),
                    complexity=getattr(strategy, 'complexity', 'medium'),
                    recommended_timeframes=getattr(strategy, 'recommended_timeframes', ['1h', '4h', '1d']),
                )

                # Apply filters
                if tag and tag not in strategy_info.tags:
                    continue
                if complexity and strategy_info.complexity != complexity:
                    continue

                all_strategies.append(strategy_info)

            except Exception as e:
                logger.warning(f"Could not load strategy {strategy_name}: {e}")
                continue

        logger.info(f"Loaded {len(all_strategies)} strategies")

        return StrategyListResponse(
            total=len(all_strategies),
            strategies=all_strategies
        )

    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}", response_model=StrategyInfo)
async def get_strategy(strategy_name: str) -> StrategyInfo:
    """
    Get detailed information about a specific strategy.

    Path Parameters:
        strategy_name: Name of the strategy

    Returns:
        Detailed strategy information
    """
    try:
        registry = get_registry()

        if strategy_name not in registry:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{strategy_name}' not found"
            )

        strategy_class = registry[strategy_name]
        strategy = strategy_class()

        try:
            params = strategy.get_parameters() if hasattr(strategy, 'get_parameters') else {}
        except:
            params = {}

        return StrategyInfo(
            name=strategy_name,
            description=strategy.__class__.__doc__ or f"{strategy_name} trading strategy",
            parameters=params,
            tags=getattr(strategy, 'tags', []),
            complexity=getattr(strategy, 'complexity', 'medium'),
            recommended_timeframes=getattr(strategy, 'recommended_timeframes', ['1h', '4h', '1d']),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting strategy {strategy_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_name}/parameters")
async def get_strategy_parameters(strategy_name: str) -> Dict[str, Any]:
    """
    Get parameter schema for a strategy.

    Path Parameters:
        strategy_name: Name of the strategy

    Returns:
        Parameter definitions with types and ranges
    """
    try:
        registry = get_registry()

        if strategy_name not in registry:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{strategy_name}' not found"
            )

        strategy_class = registry[strategy_name]
        strategy = strategy_class()

        # Get default parameters
        try:
            params = strategy.get_parameters() if hasattr(strategy, 'get_parameters') else {}
        except:
            params = {}

        # TODO: Add parameter schema/validation info
        # For now, just return the parameters
        return {
            "strategy": strategy_name,
            "parameters": params,
            "schema": {}  # Future: add parameter types, ranges, descriptions
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameters for {strategy_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
