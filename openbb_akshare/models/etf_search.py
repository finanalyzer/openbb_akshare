"""AKShare ETF Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
import logging

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field

logger = logging.getLogger(__name__)


class AKShareEtfSearchQueryParams(EtfSearchQueryParams):
    """AKShare ETF Search Query Params.
    
    Source: https://akshare.akfamily.xyz/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request.",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class AKShareEtfSearchData(EtfSearchData):
    """AKShare ETF Search Data."""

    __alias_dict__ = {
        "symbol": "代码",
        "name": "名称",
    }


class AKShareEtfSearchFetcher(
    Fetcher[
        AKShareEtfSearchQueryParams,
        List[AKShareEtfSearchData],
    ]
):
    """AKShare ETF Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEtfSearchQueryParams:
        """Transform the query."""
        return AKShareEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        # pylint: disable=import-outside-toplevel
        try:
            import akshare as ak
            
            etf_list_df = None
            api_name = None
            
            # Try multiple approaches to get ETF list
            # Approach 1: Try fund_name_em which might return fund list with code and name
            try:
                logger.debug("Trying fund_name_em API")
                # Try to get all fund names, then filter for ETFs
                fund_list_df = ak.fund_name_em()
                if fund_list_df is not None and not fund_list_df.empty:
                    logger.debug(f"fund_name_em returned columns: {list(fund_list_df.columns)}")
                    # Filter for ETF funds if there's a type column
                    if '基金代码' in fund_list_df.columns or '代码' in fund_list_df.columns:
                        # Try to filter for ETF type funds
                        etf_list_df = fund_list_df.copy()
                        api_name = 'fund_name_em'
                        logger.debug(f"Using fund_name_em with {len(etf_list_df)} rows")
            except (AttributeError, Exception) as e:
                logger.debug(f"fund_name_em failed: {str(e)}")
            
            # Approach 2: Try fund_etf_spot_em which returns ETF spot data
            # This might have code/name in the index or we need to extract from it differently
            if etf_list_df is None or etf_list_df.empty:
                try:
                    logger.debug("Trying fund_etf_spot_em API")
                    spot_df = ak.fund_etf_spot_em()
                    if spot_df is not None and not spot_df.empty:
                        logger.debug(f"fund_etf_spot_em returned columns: {list(spot_df.columns)}")
                        logger.debug(f"fund_etf_spot_em index: {list(spot_df.index.names) if spot_df.index.nlevels > 1 else spot_df.index.name}")
                        # Check if code/name is in index
                        if spot_df.index.nlevels > 0:
                            # Reset index to see if code/name is there
                            spot_df_reset = spot_df.reset_index()
                            logger.debug(f"After reset_index, columns: {list(spot_df_reset.columns)}")
                            # Use reset version if it has better columns
                            if '基金代码' in spot_df_reset.columns or '代码' in spot_df_reset.columns:
                                etf_list_df = spot_df_reset
                                api_name = 'fund_etf_spot_em_reset'
                        if etf_list_df is None:
                            # The API returns net value data, we need a different approach
                            # Maybe the data has a symbol/code embedded elsewhere
                            logger.debug("fund_etf_spot_em doesn't have code/name columns directly")
                except (AttributeError, Exception) as e:
                    logger.debug(f"fund_etf_spot_em failed: {str(e)}")
            
            # Approach 3: Try to extract from fund ETF category or other list APIs
            if etf_list_df is None or etf_list_df.empty:
                try:
                    logger.debug("Trying to get ETF list from fund_etf_category_sina or similar")
                    # Try different category/list APIs
                    category_list = ['ETF基金', '股票型ETF', '债券型ETF', '商品型ETF']
                    for category in category_list:
                        try:
                            cat_df = ak.fund_etf_category_sina(symbol=category)
                            if cat_df is not None and not cat_df.empty:
                                logger.debug(f"fund_etf_category_sina({category}) returned columns: {list(cat_df.columns)}")
                                if etf_list_df is None:
                                    etf_list_df = cat_df.copy()
                                    api_name = f'fund_etf_category_sina_{category}'
                                else:
                                    # Combine with previous data
                                    etf_list_df = pd.concat([etf_list_df, cat_df], ignore_index=True)
                                break
                        except (AttributeError, Exception):
                            continue
                except Exception as e:
                    logger.debug(f"Category-based approach failed: {str(e)}")
            
            # Approach 4: Try fund_etf_fund_info_em 
            if etf_list_df is None or etf_list_df.empty:
                try:
                    logger.debug("Trying fund_etf_fund_info_em API")
                    info_df = ak.fund_etf_fund_info_em()
                    if info_df is not None and not info_df.empty:
                        logger.debug(f"fund_etf_fund_info_em returned columns: {list(info_df.columns)}")
                        # Check index or reset
                        if info_df.index.nlevels > 0:
                            info_df_reset = info_df.reset_index()
                            if '基金代码' in info_df_reset.columns or '代码' in info_df_reset.columns:
                                etf_list_df = info_df_reset
                                api_name = 'fund_etf_fund_info_em_reset'
                        if etf_list_df is None and ('基金代码' in info_df.columns or '代码' in info_df.columns):
                            etf_list_df = info_df.copy()
                            api_name = 'fund_etf_fund_info_em'
                except (AttributeError, Exception) as e:
                    logger.debug(f"fund_etf_fund_info_em failed: {str(e)}")
            
            # If all approaches failed, return empty list
            if etf_list_df is None or etf_list_df.empty:
                logger.warning("All akshare ETF API approaches failed or returned empty data")
                return []
            
            logger.debug(f"Using API {api_name} with columns: {list(etf_list_df.columns)}")
            
            # If using fund_name_em, we may need to filter for ETFs specifically
            if api_name == 'fund_name_em' and etf_list_df is not None:
                # Try to filter for ETF type if there's a type column
                type_columns = ['基金类型', '类型', 'ftype', 'fund_type', '类型2']
                for type_col in type_columns:
                    if type_col in etf_list_df.columns:
                        # Filter for ETFs (ETF types typically contain "ETF" or specific codes)
                        etf_mask = etf_list_df[type_col].astype(str).str.contains('ETF', case=False, na=False)
                        if etf_mask.any():
                            etf_list_df = etf_list_df[etf_mask].copy()
                            logger.debug(f"Filtered to {len(etf_list_df)} ETF funds using column {type_col}")
                            break
            
            # Check if required columns exist, if not try alternative column names
            required_cols = ['代码', '名称']
            col_mapping = {}
            
            # Check if required columns exist directly
            if not all(col in etf_list_df.columns for col in required_cols):
                logger.debug(f"Required columns {required_cols} not found, attempting column mapping")
                logger.debug(f"Available columns: {list(etf_list_df.columns)}")
                
                # Try to find columns with similar names
                for req_col in required_cols:
                    # Try exact match first
                    if req_col in etf_list_df.columns:
                        col_mapping[req_col] = req_col
                        logger.debug(f"Found exact match for {req_col}")
                        continue
                    
                    # Simple direct matching without lambda to avoid closure issues
                    found = False
                    col_str_list = [str(col) for col in etf_list_df.columns]
                    
                    if req_col == '代码':
                        # For code/symbol, try these patterns in order of priority
                        patterns_to_match = ['基金代码', 'fund_code', '代码', 'code', 'symbol', '证券代码']
                    else:  # req_col == '名称'
                        # For name, try these patterns in order of priority
                        patterns_to_match = ['基金简称', '基金名称', '简称', '名称', 'short_name', 'name', 'fund_name']
                    
                    for pattern in patterns_to_match:
                        for col in etf_list_df.columns:
                            col_str = str(col)
                            # Skip if already mapped to another required column
                            if col_str in col_mapping.values():
                                continue
                            
                            # Check if pattern matches
                            if pattern.lower() in col_str.lower() or pattern in col_str:
                                col_mapping[req_col] = col
                                logger.debug(f"Found pattern match for {req_col}: '{col}' (pattern: {pattern})")
                                found = True
                                break
                        
                        if found:
                            break
                    
                    if not found:
                        logger.warning(f"Could not find match for {req_col} in columns: {list(etf_list_df.columns)}")
                
                # Log the mapping result before checking
                logger.debug(f"Column mapping result: {col_mapping}")
                logger.debug(f"Required columns: {required_cols}")
                
                # If we still can't find both required columns, log and return empty list
                if len(col_mapping) < 2:
                    logger.warning(f"Could not map required columns. Found mapping: {col_mapping}, Available columns: {list(etf_list_df.columns)}")
                    logger.warning(f"First few rows of data:\n{etf_list_df.head() if not etf_list_df.empty else 'Empty DataFrame'}")
                    return []
                
                # Rename columns to match expected names
                # Note: pandas rename expects {old_name: new_name}, so we need to reverse the mapping
                # Our col_mapping is {required_col: actual_col}, so reverse it to {actual_col: required_col}
                rename_mapping = {v: k for k, v in col_mapping.items()}
                logger.debug(f"Renaming columns with mapping: {rename_mapping}")
                try:
                    etf_list_df = etf_list_df.rename(columns=rename_mapping)
                    logger.debug(f"After rename, columns are: {list(etf_list_df.columns)}")
                    
                    # Verify the rename was successful
                    if not all(col in etf_list_df.columns for col in required_cols):
                        logger.error(f"Rename failed! Required columns {required_cols} not found after rename.")
                        logger.error(f"Actual columns after rename: {list(etf_list_df.columns)}")
                        logger.error(f"Mapping used: {rename_mapping} (from {col_mapping})")
                        return []
                except Exception as e:
                    logger.error(f"Error renaming columns: {str(e)}, mapping: {rename_mapping}")
                    import traceback
                    logger.error(traceback.format_exc())
                    return []
            
            # Final check: Ensure we only have the required columns
            if not all(col in etf_list_df.columns for col in required_cols):
                logger.warning(f"Required columns still missing after mapping. Required: {required_cols}, Available: {list(etf_list_df.columns)}")
                logger.warning(f"This should not happen if mapping was successful. Checking mapping again...")
                # Double check the mapping
                missing_cols = [col for col in required_cols if col not in etf_list_df.columns]
                logger.warning(f"Missing columns: {missing_cols}")
                return []
            
            # Select only the required columns
            etf_list_df = etf_list_df[required_cols].copy()
            
            # Apply query filter if provided
            if query.query:
                query_lower = query.query.lower()
                # Filter by code or name
                mask = (
                    etf_list_df['代码'].astype(str).str.lower().str.contains(query_lower, na=False) |
                    etf_list_df['名称'].astype(str).str.lower().str.contains(query_lower, na=False)
                )
                etf_list_df = etf_list_df[mask]
                
            # Apply limit if specified
            if query.limit is not None and query.limit > 0:
                etf_list_df = etf_list_df.head(query.limit)
            
            # Convert to list of dictionaries
            result = etf_list_df.to_dict(orient="records")
            logger.debug(f"Returning {len(result)} ETF records")
            return result
                
        except Exception as e:
            # Log the exception for debugging
            logger.exception(f"Error in aextract_data: {str(e)}")
            # If akshare doesn't support ETF search or any error occurs,
            # return empty list to prevent 422 errors
            return []

    @staticmethod
    def transform_data(
        query: AKShareEtfSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareEtfSearchData]:
        """Transform the data."""
        if not data:
            return []
        return [AKShareEtfSearchData.model_validate(d) for d in data]

