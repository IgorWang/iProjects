# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/9/7

import xml.etree.ElementTree as etree
import json


class JSONConnector:
    def __init__(self, filepath):
        self.data = dict()
        with open(filepath, 'r', encoding="utf8") as f:
            self.data = json.load(f)

    @property
    def parsed_data(self):
        return self.data


class XMLConnector:
    def __init__(self, filepath):
        self.tree = etree.parse(filepath)

    @property
    def parsed_data(self):
        return self.tree


def connection_factory(filepath):
    '''
    A Factory Method
    :return: instance of JSONConnector or XMLConnector
            depending on the extension of the input file path as follows
    '''
    if filepath.endswith("json"):
        connector = JSONConnector
    elif filepath.endswith("xml"):
        connector = XMLConnector
    else:
        raise ValueError("Cannot connector to {}".format(filepath))

    return connector(filepath)


def connect_to(filepath):
    '''
    A wrapper of connection_factory()
    adds exception handling
    '''
    factory = None
    try:
        factory = connection_factory(filepath)
    except ValueError as ve:
        print(ve)
    return factory


def main():
    '''
    demonstrates how the factory method design pattern can be used
    '''

    sqlite_factory = connect_to("person.sq3")
    print(sqlite_factory)
    xml_factory = connect_to("person.xml")
    xml_data = xml_factory.parsed_data
    liars = xml_data.findall(".//person[lastName='{}']".format('Liar'))
    print("found: {} persons".format(len(liars)))
    for liar in liars:
        print('first name: {}'.format(liar.find('firstName').text))
        print('last name: {}'.format(liar.find('lastName').text))
        [print('phone number ({}):'.format(p.attrib['type']), p.text) for p in liar.find('phoneNumbers')]
    print()

    json_factory = connect_to('donut.json')
    json_data = json_factory.parsed_data
    print('found: {} donuts'.format(len(json_data)))
    for donut in json_data:
        print('name: {}'.format(donut['name']))
        print('price: ${}'.format(donut['ppu']))
        [print('topping: {} {}'.format(t['id'], t['type'])) for t in donut['topping']]


if __name__ == '__main__':
    main()
