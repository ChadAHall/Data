import sys
import reader
import poi_emails

def make_fraction(numerator, denominator):
    try:
        fraction = numerator / denominator
    except TypeError:
        fraction = 'NaN'
    return fraction

def from_poi(person_values):
    #this function calculates the fraction of messages from POI to this person
    poi_messages = person_values['from_poi_to_this_person']
    all_messages = person_values['to_messages']
    return {'fraction_from-poi': make_fraction(poi_messages, all_messages)}

def to_poi(person_values):
    #function to calculate the fraction of messages from this person to poi
    poi_messages = person_values['from_this_person_to_poi']
    all_messages = person_values['from_messages']
    return {'fraction_to_poi': make_fraction(poi_messages, all_messages)}

def shared_poi(person_values):
    # this function is used to calculate the fraction that the person
    # sreceived from poi and how many shared recipient with a poi
    poi_messages = person_values['shared_receipt_with_poi']
    all_messages = person_values['to_messages']
    return {'fraction_shared'}: make_fraction(poi_message, all_messages)
