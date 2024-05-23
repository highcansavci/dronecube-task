from sqlalchemy.inspection import inspect


class Serializer(object):

    def serialize(self):
        attr = dict()
        for c in inspect(self).attrs.keys():
            if c == "global_position" or c == "velocity":
                attr.update(getattr(self, c).serialize())
            elif c == "home_position":
                home_dict = getattr(self, c).serialize()

                def change_key(key):
                    return "home_" + key

                attr.update(dict((change_key(k), v) for k, v in home_dict.items()))
            else:
                attr[c] = getattr(self, c)
        return attr

    def serialize_base(self):
        return self.__dict__

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
