# pylint: disable=too-few-public-methods, consider-using-f-string
"""User Querys"""

import json
from typing import List, Tuple

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text

from src.database.db_connection import db_connector
from src.database.models import Motorists
from src.database.models.runs import runs_factory


class MotoristsQuerys:
    """A Consult if name alredy exits"""

    @classmethod
    @db_connector
    def show(cls, connection) -> List:
        """Return all motorists in database"""
        return connection.session.query(Motorists).all()

    @classmethod
    @db_connector
    def check_name(cls, connection, name: str):
        """Check with name already exists in database."""
        return connection.session.query(Motorists).filter_by(name=name).first()

    @classmethod
    @db_connector
    def new(cls, connection, name, data_json):
        """someting"""
        check_name = connection.session.query(Motorists).filter_by(name=name).first()
        if check_name == None:  # pylint: disable=singleton-comparison
            new_user = Motorists(name=name, data_json=data_json)
            connection.session.add(new_user)
            connection.session.commit()

    @classmethod
    @db_connector
    def get_id(cls, connection, motorist_id):
        """Get a driver by id."""
        return connection.session.query(Motorists).filter_by(id=motorist_id).first()

    @classmethod
    @db_connector
    def delete(cls, connection, motorist_id) -> None:
        """Delete a driver by id"""
        driver = connection.session.query(Motorists).filter_by(id=motorist_id).first()
        connection.session.delete(driver)
        connection.session.execute(text(
            f"DROP TABLE IF EXISTS runs_{driver.name};"
            )
        )
        connection.session.commit()

    @classmethod
    @db_connector
    def delete_all(cls, connection) -> None:
        """Delete a driver by id"""
        drivers = connection.session.query(Motorists).all()

        for driver in drivers:
            try:
                connection.session.delete(driver)
                connection.session.execute(text(
                f"DROP TABLE IF EXISTS runs_{driver.name};"
                    )
                )
                connection.session.commit()

            except Exception as error:
                print(error)

        connection.session.commit()

    @classmethod
    @db_connector
    def create_motorists_runs(cls, connection, name):
        """Create a table to archive driver runs"""
        connection.session.execute(
            "CREATE TABLE IF NOT EXISTS {}("
            "date_time DATETIME UNIQUE, "
            "valor INTEGER(11) NOT NULl, "
            "operator VARCHAR(1));".format(name.replace(" ", "_"))
        )
        connection.session.commit()

    @classmethod
    @db_connector
    def get_group(cls, connection, name) -> Tuple:
        """Return the group to which a driver belongs"""
        driver: Motorists = (
            connection.session.query(Motorists).filter_by(name=name).first()
        )
        group: json = driver.data_json
        return group["comission"]

    @classmethod
    @db_connector
    def update_tag(cls, connection, _id, comission) -> Tuple:
        """Update driver group"""
        driver: Motorists = (
            connection.session.query(Motorists).filter_by(id=_id).first()
        )
        driver.data_json["tag"] = comission
        flag_modified(driver, "data_json")
        connection.session.commit()
