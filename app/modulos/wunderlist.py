#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from wunderpy import Wunderlist


# https://github.com/bsmt/wunderpy

w = Wunderlist()
w.login("username", "password")
w.update_lists()  # you have to run this first, before you do anything else

w.add_list("test")  # make a new list called "test"

due = datetime.now().isoformat()
w.add_task("test wunderpy", list_title="test", note="a note",
           due_date=due, starred=True)  # add a task to it
w.complete_task("test wunderpy", "test")  # complete it
w.delete_task("test wunderpy", "test")  # and delete it

w.delete_list("test")  # and delete the list
