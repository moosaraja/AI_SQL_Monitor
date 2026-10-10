import pyodbc


SERVER = "localhost"
DATABASE = "master"
DRIVER = "ODBC Driver 17 for SQL Server"


def get_connection():
    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


if __name__ == "__main__":
    connection = get_connection()

    print("Connected to SQL Server successfully!")

    connection.close()