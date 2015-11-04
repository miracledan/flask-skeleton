# -*- coding: utf-8 -*-

import json

class PeeweeJsonSerializer(object):
    __json_hidden__ = None

    def to_json(self):
        for k in self.__dict__.keys():
            if k not in ['_data', '_obj_cache', '_dirty']:
                self._data[k] = self.__dict__[k]

        data = json.dumps(self, default=lambda o: self._try(o), sort_keys=True, indent=0, separators=(',',':')).replace('\n', '')
        
        hidden = self.__json_hidden__ or []
        dic = json.loads(data)
        for k,v in dic.items():
            if k in hidden:
                dic.pop(k)
        return dic

    @staticmethod
    def _try(o): 
        try: 
            return o.__dict__["_data"]
        except:
            return str(o)