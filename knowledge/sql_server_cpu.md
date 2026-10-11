
# SQL Server High CPU Troubleshooting

## Symptoms
SQL Server CPU utilization remains consistently high.
Queries may become slower, and response times may increase.

## Possible Causes
- Expensive queries consuming excessive CPU
- Missing or inefficient indexes
- Outdated statistics
- Poor execution plans
- Excessive query compilations or recompilations
- High concurrent query workload
- Parallelism-related CPU pressure
- External processes competing for CPU resources

## Initial DBA Investigation
1. Verify whether SQL Server or another process is consuming CPU.
2. Review SQL Server CPU trends over several minutes.
3. Identify queries with high total_worker_time in sys.dm_exec_query_stats.
4. Review currently executing requests in sys.dm_exec_requests.
5. Examine execution plans for expensive operators.
6. Check relevant wait statistics.
7. Investigate compilation rates and plan cache behavior.
8. Review statistics, indexes and parallelism configuration.

## Useful SQL Server DMVs
- sys.dm_os_ring_buffers
- sys.dm_exec_requests
- sys.dm_exec_query_stats
- sys.dm_exec_sql_text
- sys.dm_exec_query_plan
- sys.dm_os_wait_stats
- sys.dm_os_schedulers

## Recommendations
- Identify the actual CPU-consuming workload before making changes.
- Optimize expensive queries based on execution plans and evidence.
- Update statistics when stale statistics are demonstrated.
- Evaluate missing-index suggestions rather than applying them blindly.
- Review MAXDOP and cost threshold for parallelism when appropriate.
- Avoid restarting SQL Server merely to reduce CPU utilization.

## Important Cautions
High CPU does not automatically mean missing indexes.
High CPU can result from application workload or external processes.
Historical DMV statistics may reset after SQL Server restarts.
Query statistics are cumulative and require careful interpretation.
Avoid automatic query termination without DBA approval.
