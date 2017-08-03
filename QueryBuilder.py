""" A simple Query building system created for an university assignment. 
    Igor Samurovic SL23/13 - FTN - Novi Sad - Serbia """
from weakref import WeakKeyDictionary
from collections import Iterable

class Query():
    """ The main Query class. Used to instantiate and format new Queries. """

    class QueryPart(object):
        """ Corresponds to parts of the Query object. """

        def __init__(self, keyword, separator=","):
            """ Initializes the value of the encapsulated attribute. """
            self.keyword = keyword
            self.separator = " %s " % (separator, )
            self.default = ""
            self.data = WeakKeyDictionary()

        def __get__(self, instance, objtype):
            """ Gets the value of the encapsulated attribute. """
            if self.data[instance] != self.default:
                return "%s %s" % (self.keyword, self.data[instance])
            return ""

        def format_string(self, string):
            """ Formats the QueryPart string to remove artifacts. """
            return string.replace(" , ", ", ")

        def __set__(self, instance, value):
            """ Sets the value of the encapsulated attribute. """
            if isinstance(value, str):
                self.data[instance] = value
            elif isinstance(value, Iterable):
                self.data[instance] = self.format_string(self.separator.join(value))
            else:
                self.data[instance] = ""

    def where_and(self, value):
        """ Appends an entry with the AND conditional to the "where" part of the query.
            Returns the Query object. """
        if self.where_part:
            self.where_part += " AND %s" % (value, )
        else:
            self.where_part += "WHERE %s"  % (value, )
        return self

    def where_or(self, value):
        """ Appends an entry with the OR conditional to the "where" part of the query.
            Returns the Query object. """
        if self.where_part:
            self.where_part += " OR %s" % (value, )
        else:
            self.where_part += "WHERE %s"  % (value, )
        return self

    def query_string(self, data=None):
        """ Joins all parts of the query. Attempts to replace temporary parts of the query (denoted as starting with ":") with the dictionary entries.
            Returns the joined and formatted query string. """
        self._query_string = " ".join([self.select_part, self.where_part, self.order_by_part, self.limit_part])
        if isinstance(data, dict):
            for key in data.keys():
                self._query_string = self._query_string.replace(":%s" % (key,), "'%s'" % (data[key], ))
        return self._query_string

    def select(self, val):
        """ Sets the "select" part of the query up until "where". If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined.
        Potential joins are to be added in this section.
        Returns the Query object. """
        self.select_part = val
        return self

    def where(self, val):
        """ Sets the "where" part of the query up until "order by". If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined.
        Returns the Query object. """
        self.where_part = val
        return self

    def order_by(self, val):
        """ Sets the "order by" part of the query up until "limit". If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined.
        Returns the Query object. """
        self.order_by_part = val
        return self

    def limit(self, val):
        """ Sets the "limit" part of the query. If the passed value is a string, it is combined with a keyword
        without any formatting. If the passed value is a collection, it will be formatted and joined.
        Returns the Query object. """
        self.limit_part = val
        return self

    select_part = QueryPart("SELECT")
    where_part = QueryPart("WHERE", "AND")
    order_by_part = QueryPart("ORDER BY")
    limit_part = QueryPart("LIMIT")

    def apply_dict_data(self, data):
        """ Applies the dictionary entries to fitting query parts. """
        self.select_part = data["select"] if data["select"] else None
        self.where_part = data["where"] if data["where"] else None
        self.order_by_part = data["order_by"] if data["order_by"] else None
        self.limit_part = data["limit"] if data["limit"] else None

    def __init__(self, data=None):
        """ Initializes a new Query object. """
        self._query_string = ""
        self.select_part = None
        self.where_part = None
        self.order_by_part = None
        self.limit_part = None

        if data and isinstance(data, dict):
            self.apply_dict_data(data)


#Testing
def test():
    """ A simple function used for testing. """
    tmp = Query().select("* FROM USER u").where(["u.id = :id", "u.avg > :avg"]).order_by("u.id ASC").limit(["10", "5"])

    print(tmp.query_string({"id": 5, "avg": 6.6}))

test()
