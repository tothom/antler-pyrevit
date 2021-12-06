# -*- coding: utf-8 -*-

from System.Collections.Generic import *
from rpw import revit, DB, UI

from pyrevit import forms, script
from pyrevit import EXEC_PARAMS

from collections import OrderedDict

from Autodesk.Revit.Exceptions import InvalidOperationException

logger = script.get_logger()
output = script.get_output()

relinquish_options = DB.RelinquishOptions(False)

options = OrderedDict()

options["Elements checked out by the current user should be relinquished."] = 'CheckedOutElements'
options["Family worksets owned by the current user should be relinquished."] = 'FamilyWorksets'
options["Project standards worksets owned by the current user should be relinquished."] = 'StandardWorksets'
options["User-created worksets owned by the current user should be relinquished."] = 'UserWorksets'
options["View worksets owned by the current user should be relinquished."] = 'ViewWorksets'


selected = forms.SelectFromList.show(
    options.keys(),
    title="Select relinquish options",
    multiselect=True
)

for a in selected:
    setattr(relinquish_options, options[a], True)


transact_options = DB.TransactWithCentralOptions()
sync_options = DB.SynchronizeWithCentralOptions()
sync_options.SetRelinquishOptions(relinquish_options)

# print(
# 	sync_options.RelinquishBorrowedElements,
# 	sync_options.RelinquishFamilyWorksets,
# 	sync_options.RelinquishProjectStandardWorksets,
# 	sync_options.RelinquishUserCreatedWorksets,
# 	sync_options.RelinquishViewWorksets,
# 	sync_options.SaveLocalAfter,
# 	sync_options.SaveLocalBefore,
# 	sync_options.SaveLocalFile
# 	)

docs_to_sync = [
    doc for doc in revit.docs if doc.IsWorkshared and not doc.IsLinked]

print("Synchronising {0} docs...".format(len(docs_to_sync)))
output.indeterminate_progress(True)

for i, doc in enumerate(docs_to_sync):
    print("Trying to synchronize {0}...".format(doc.Title))

    try:
        doc.SynchronizeWithCentral(transact_options, sync_options)
        print("Document synchronized!")
    except Exception as e:
        logger.warning("Document NOT synchronized!")
        logger.debug(type(e), e)
    else:
        if EXEC_PARAMS.config_mode:
            try:
                doc.Close()
            except InvalidOperationException as e:
                close_doc = UI.RevitCommandId.LookupPostableCommandId(
                    UI.PostableCommand.Close)
                revit.uiapp.PostCommand(close_doc)

        #     logger.warning(e.Message)

    output.indeterminate_progress(False)
    output.update_progress(i + 1, len(docs_to_sync))

print("Done! 👍")