# -*- coding: utf-8 -*-
#
# Copyright 2016 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from logbook import Logger
from logbook.more import ColorizedStderrHandler



__all__ = [
    "log",
]


def log_formatter(record, handler):
    return "{level}: {msg}".format(
        level=record.level_name,
        msg=record.message,
    )


# handler = StreamHandler(sys.stdout)
handler = ColorizedStderrHandler()
handler.formatter = log_formatter
handler.push_application()


log = Logger("log")


def user_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "")

    message = sep.join(map(str, args)) + end

    log.info(message)

