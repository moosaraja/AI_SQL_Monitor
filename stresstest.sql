USE Vehicle;
GO

SET NOCOUNT ON;

DECLARE @StartTime DATETIME2 = SYSDATETIME();
DECLARE @DurationSeconds INT = 60;
DECLARE @Iteration BIGINT = 0;
DECLARE @Result BIGINT;

WHILE DATEDIFF(SECOND, @StartTime, SYSDATETIME()) < @DurationSeconds
BEGIN
    SELECT @Result = COUNT_BIG(*)
    FROM
    (
        SELECT TOP (50000)
            a.[VIN (1-10)]
        FROM dbo.Electric_Vehicle_Population_Data AS a
        CROSS JOIN dbo.Electric_Vehicle_Population_Data AS b
        WHERE CHECKSUM(
            CONCAT(
                a.[VIN (1-10)],
                b.[VIN (1-10)],
                @Iteration
            )
        ) % 17 = 0
    ) AS CPUStress;

    SET @Iteration += 1;
END;

SELECT
    @Iteration AS iterations_completed,
    DATEDIFF(SECOND, @StartTime, SYSDATETIME())
        AS duration_seconds,
    @Result AS last_result;