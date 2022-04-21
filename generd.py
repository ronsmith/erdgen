import click
import ssl
from typing import List
from dataclasses import dataclass, field
from pg8000 import native


@dataclass
class Attribute:
    name: str
    ord: int
    type: str
    nullable: bool
    max_len: int


@dataclass
class Entity:
    name: str
    attributes: List[Attribute] = field(default_factory=list)


@click.command()
@click.option('--host', '-h', required=True)
@click.option('--port', '-p', required=True, default=5432, type=int)
@click.option('--database', '-d', required=True)
@click.option('--username', '-u', required=True)
@click.option('--password', '-w', required=True)
@click.option('--schema', '-s', required=True)
def main(host, port, database, username, password, schema):
    # noinspection PyUnresolvedReferences,PyProtectedMember
    ssl_ctx = ssl._create_unverified_context()
    with native.Connection(username, host, database, port, password, ssl_context=ssl_ctx) as conn:
        results = conn.run("""
                SELECT table_name, column_name, ordinal_position, data_type, is_nullable, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = :schema
                ORDER BY table_name, ordinal_position;
            """, schema=schema)

        entities = {}

        for row in results:
            if row[0] not in entities:
                entities[row[0]] = Entity(row[0])
            entity = entities[row[0]]
            entity.attributes.append(Attribute(row[1], row[2], row[3], row[4] == 'YES', row[5]))

        print('@startuml')
        for entity in entities.values():
            print('entity', entity.name, '{')
            for attrib in entity.attributes:
                print('  ', attrib.name, ':', attrib.type, '<<NULLABLE>>' if attrib.nullable else '')
            print('}')
        print('@endurl')


if __name__ == '__main__':
    main()

