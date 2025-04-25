import utils.database_helper_methods
from services import create_inventory_params_development_db_table
from services import create_routing_development_db_tables
from services import create_sku_order_development_db_table
from utils.settings import settings


def main():
    try:
        print("Starting the database population process...")
        # Create 'Development' DB user (if does not exist)
        privileges = "SELECT, INSERT, CREATE, INDEX, ALTER, REFERENCES"
        utils.database_helper_methods.create_db_user(settings.db_username,
                                                     "%",
                                                     settings.db_password,
                                                     privileges
                                                     )
        # Create tables
        create_sku_order_development_db_table.main()
        create_inventory_params_development_db_table.main()
        create_routing_development_db_tables.main()

        print("\n" + "All services attempted.")
    except Exception as e:
        print("\n" + "Critical error in the main script:", str(e))


if __name__ == "__main__":
    main()
