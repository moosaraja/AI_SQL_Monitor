import xml.etree.ElementTree as ET
import hashlib

from db_connection import get_connection


SYSTEM_HEALTH_FILE = (
    r"D:\MSSQL\MSSQL16.MSSQLSERVER\MSSQL\Log\system_health*.xel"
)


def get_deadlock_event_id(file_name, file_offset):

    value = f"{file_name}:{file_offset}"

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def parse_deadlock(event_xml):

    root = ET.fromstring(event_xml)

    deadlock = root.find(".//deadlock")

    if deadlock is None:
        return None

    victim_process = deadlock.find(
        "./victim-list/victimProcess"
    )

    victim_id = None

    if victim_process is not None:
        victim_id = victim_process.get("id")

    processes = []

    for process in deadlock.findall(
        "./process-list/process"
    ):

        process_data = {
            "id": process.get("id"),
            "spid": process.get("spid"),
            "ecid": process.get("ecid"),
            "status": process.get("status"),
            "hostname": process.get("hostname"),
            "loginname": process.get("loginname"),
            "clientapp": process.get("clientapp"),
            "isolationlevel": process.get("isolationlevel"),
            "waitresource": process.get("waitresource"),
            "waittime": process.get("waittime"),
            "transactionname": process.get("transactionname"),
            "lasttranstarted": process.get("lasttranstarted"),
        }

        inputbuf = process.find("./inputbuf")

        if inputbuf is not None:
            process_data["sql_text"] = (
                inputbuf.text.strip()
                if inputbuf.text
                else None
            )
        else:
            process_data["sql_text"] = None

        processes.append(process_data)

    resources = []

    for resource in deadlock.findall(
        "./resource-list/*"
    ):

        resource_data = {
            "resource_type": resource.tag,
            "resource_id": resource.get("id"),
            "objectname": resource.get("objectname"),
            "dbid": resource.get("dbid"),
            "associatedobjectid": resource.get(
                "associatedObjectId"
            )
        }

        owners = []

        for owner in resource.findall(
            "./owner-list/owner"
        ):

            owners.append({
                "id": owner.get("id"),
                "mode": owner.get("mode"),
            })

        waiters = []

        for waiter in resource.findall(
            "./waiter-list/waiter"
        ):

            waiters.append({
                "id": waiter.get("id"),
                "mode": waiter.get("mode"),
                "requestType": waiter.get(
                    "requestType"
                ),
            })

        resource_data["owners"] = owners
        resource_data["waiters"] = waiters

        resources.append(resource_data)

    return {
        "victim_process_id": victim_id,
        "processes": processes,
        "resources": resources,
    }


def get_deadlocks():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        query = """
        SELECT
            timestamp_utc,
            file_name,
            file_offset,
            CAST(event_data AS XML) AS event_data
        FROM sys.fn_xe_file_target_read_file(
            ?,
            NULL,
            NULL,
            NULL
        )
        WHERE object_name = N'xml_deadlock_report'
        ORDER BY timestamp_utc DESC;
        """

        cursor.execute(
            query,
            SYSTEM_HEALTH_FILE
        )

        rows = cursor.fetchall()

        deadlocks = []

        for row in rows:

            timestamp_utc = row[0]
            file_name = row[1]
            file_offset = row[2]
            event_data = row[3]

            if hasattr(event_data, "value"):
                event_xml = event_data.value
            else:
                event_xml = str(event_data)

            parsed_deadlock = parse_deadlock(
                event_xml
            )

            if parsed_deadlock is None:
                continue

            deadlock = {
                "event_id": get_deadlock_event_id(
                    file_name,
                    file_offset
                ),
                "deadlock_time": timestamp_utc.isoformat(),
                "file_name": file_name,
                "file_offset": file_offset,
                "deadlock": parsed_deadlock,
                "event_xml": event_xml
            }

            deadlocks.append(deadlock)

        return deadlocks

    finally:

        connection.close()


if __name__ == "__main__":

    print("\n========== DEADLOCK COLLECTOR ==========\n")

    deadlocks = get_deadlocks()

    print(
        f"Deadlocks found: {len(deadlocks)}"
    )

    for deadlock in deadlocks:

        print(
            f"\nDeadlock time: "
            f"{deadlock['deadlock_time']}"
        )

        parsed = deadlock["deadlock"]

        print(
            f"Victim process: "
            f"{parsed['victim_process_id']}"
        )

        print("\nProcesses:")

        for process in parsed["processes"]:

            print(
                f"\n  SPID: {process['spid']}"
            )

            print(
                f"  Host: {process['hostname']}"
            )

            print(
                f"  Login: {process['loginname']}"
            )

            print(
                f"  Application: {process['clientapp']}"
            )

            print(
                f"  Wait resource: "
                f"{process['waitresource']}"
            )

            print(
                f"  SQL: {process['sql_text']}"
            )

        print("\nResources:")

        for resource in parsed["resources"]:

            print(
                f"\n  Type: "
                f"{resource['resource_type']}"
            )

            print(
                f"  Object: "
                f"{resource['objectname']}"
            )

            print(
                f"  Database ID: "
                f"{resource['dbid']}"
            )

            print(
                f"  Owners: "
                f"{resource['owners']}"
            )

            print(
                f"  Waiters: "
                f"{resource['waiters']}"
            )

    print(
        "\n========================================\n"
    )