SELECT
    created_block_number AS created_block,
    t2.created_timestamp AS token_created_time,
    dp.created_timestamp AS pool_created_time,
    dp.contract_address AS pool_address,
    exchange_name,
    contract_version,
    verified_token AS token_paired_address,
    t.decimals AS verified_decimals,
    t.symbol AS verified_symbol,
    unverified_token AS token_address,
    t2.name,
    t2.symbol AS unverified_symbol,
    creator_address AS token_owner
FROM
    ethereum.dex_pools dp
    CROSS JOIN UNNEST(token_addresses) AS verified_token
    JOIN ethereum.tokens t ON t.contract_address = verified_token
    AND t.verified = TRUE
    CROSS JOIN UNNEST(token_addresses) AS unverified_token
    JOIN ethereum.tokens t2 ON t2.contract_address = unverified_token
    AND t2.verified = FALSE
WHERE
    t2.contract_address = '{{contract_address}}'
