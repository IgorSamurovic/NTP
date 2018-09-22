""" A simple Query building system created for an university assignment. 
    Igor Samurovic SL23/13 - FTN - Novi Sad - Serbia """
from weakref import WeakKeyDictionary
from collections import Iterable
import re

class Query():
    """ The main Query class.
    To be treated as an abstract class and not directly instantiated. """

    class Part(object):
        """ Corresponds to parts of the Query object preceeded by keywords (such as INSERT, LIMIT, etc). """

        def __init__(self, keyword, separator=","):
            """ Initializes the value of the encapsulated attribute. """
            self.keyword = keyword
            self.separator = " %s " % (separator, )
            self.default = ""
            self.data = WeakKeyDictionary()

        def __get__(self, instance, objtype):
            """ Gets the value of the encapsulated attribute. If no data has been added, then it will be assumed the part
                ultimatelly is not used, thus returning an empty string. """
            if self.data[instance] != self.default:
                if len(self.keyword) > 0:
                    return "%s %s" % (self.keyword, self.data[instance])
                else:
                    # if it's a dummy keyword return the data only
                    return self.data[instance]
            return ""

        def format_string(self, string):
            """ A helper method that formats the string to remove artifacts. """
            return re.sub(' +',' ', string.replace(" , ", ", "))

        def __set__(self, instance, value):
            """ Sets the value of the encapsulated attribute. """
            if isinstance(value, str):
                self.data[instance] = self.format_string(value)
            elif isinstance(value, Iterable):
                self.data[instance] = self.format_string(self.separator.join(x for x in value if len(x) > 0))
            else:
                self.data[instance] = ""

    def format(self, parts, data=None):
        """ Formats the input string or iterable using a provided dictionary, :%s values will be replaced by provided values. """
        if isinstance(parts, str):
            string = parts
        elif isinstance(parts, Iterable):
            string = " ".join(x for x in parts if len(x) > 0)
        else:
            string = ""

        if data is not None:
            if isinstance(data, dict):
                for key in data.keys():
                    string = string.replace(":%s" % (key,), "'%s'" % (data[key], ))
            else:
                raise TypeError("If provided, the Data argument must be a dictionary.")
        return string


class Condition():
    where_part = Query.Part("WHERE", "AND")

    def where(self, val):
        """ Sets the "where" part of the query up until "order by". If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined with ANDs.
        Returns the Query object. """
        self.where_part = val
        return self

    def _or(self, val, predicate_check = True):
        if predicate_check:
            self.where_part += " OR " + val
        return self

    def _and(self, val, predicate_check = True):
        if predicate_check:
            self.where_part += " AND " + val
        return self

    def where_id(self, id = ":id"):
        """ Sets the "where" part to simply be an identificator. """
        if id != ":id":
            try:
                if int(id) != float(id):
                    raise TypeError("ID value must be an integer.")
            except:
                raise TypeError("ID value must be an integer.")
                
        self.where_part = "id == %s" % (id, )
        return self

class SelectQuery(Query, Condition):
    select_part = Query.Part("SELECT")
    order_by_part = Query.Part("ORDER BY")
    order_part = Query.Part("")
    limit_part = Query.Part("LIMIT")

    def __init__(self, select_part_text):
        if select_part_text is not None:
            self.select_part = select_part_text

    def render(self, data):
        """ Renders the query to string considering the data provided for formatting. """
        return self.format([self.select_part, self.where_part, self.order_by_part, self.order_part, self.limit_part], data)

    def order_by(self, columns, asc):
        """ Sets the "order by" part of the query up until "limit". If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined. The asc boolean argument decides the order.
        Returns the Query object. """
        self.order_by_part = columns
        if asc == True:
            self.order_part = "ASC"
        else:
            self.order_part = "DESC"
        return self

    def limit(self, val, offset=None):
        """ Sets the "limit" part of the query. Value and offset arguments are each checked and passed into the query.
        Returns the Query object. """

        text = ""
        try:
            part = int(val)
            if int(val) != float(val):
                raise TypeError("Limit value must be an integer.")
        except:
            raise TypeError("Limit value must be an integer.")

        text = str(val)
        
        if offset is not None:
            try:
                offset = int(offset)
            except:
                raise TypeError("Offset value must be an integer.")

            text += ", " + str(offset)
        
        self.limit_part = text
        return self

class InsertQuery(Query, Condition):
    insert_part = Query.Part("INSERT INTO")
    values_part = Query.Part("VALUES")

    def __init__(self, table_name, columns):
        self.insert_part = table_name + " (" + ", ".join(columns) + ")"
        self.values_part = "(" + ", ".join(":" + x for x in columns) + ")"        

    def render(self, data):
        return self.format([self.insert_part, self.values_part], data)

class UpdateQuery(Query, Condition):
    update_part = Query.Part("UPDATE")
    values_part = Query.Part("SET")

    def __init__(self, table_name, columns):
        self.update_part = table_name
        self.values_part = ((x + " = :" + x) for x in columns)

    def render(self, data):
        return self.format([self.update_part, self.values_part, self.where_part], data)

class UpdateQuery(Query, Condition):
    update_part = Query.Part("UPDATE")
    values_part = Query.Part("SET")

    def __init__(self, table_name, columns):
        self.update_part = table_name
        self.values_part = ((x + " = :" + x) for x in columns)

    def render(self, data):
        return self.format(" ".join([self.update_part, self.values_part, self.where_part]), data)

class DeleteQuery(Query, Condition):
    delete_part = Query.Part("DELETE FROM")

    def __init__(self, table_name):
        self.delete_part = table_name

    def render(self, data):
        return self.format(" ".join([self.delete_part, self.where_part]), data)

# Testing block
if __name__ == "__main__":
    
    query = InsertQuery("USER", ["name", "surname"])
    print(query.render({"name": "igor", "surname": "samurovic"}))

    query = UpdateQuery("USER", ["name", "surname"]).where_id(5)
    print(query.render({"name" : "Rogi", "surname" : "Civorumas", "id" : 1}))

    grades_matter = True
    query = SelectQuery("* FROM USER u").where("u.id == :id")._and("(u.avg > :avg1 AND u.avg < :avg2)", grades_matter).order_by(["u.name", "u.surname"], True).limit(10)
    print(query.render({"id": 5, "avg1": 6.6, "avg2": 9.2}))

    query = DeleteQuery("USER").where_id()
    print(query.render({"id":5}))

