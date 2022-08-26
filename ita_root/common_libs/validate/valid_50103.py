#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from flask import g


def menu_column_group_valid(objdbca, objtable, option):
    retBool = True
    msg = ''

    user_env = g.LANGUAGE.upper()
    entry_parameter = option.get('entry_parameter').get('parameter')
    current_parameter = option.get('current_parameter').get('parameter')
    cmd_type = option.get("cmd_type")
    
    # ---------親カラムグループ---------
    parent_column_group = entry_parameter.get("parent_column_group")
    entry_uuid = entry_parameter.get("uuid")
    column_group_name = current_parameter.get("uuid")
    # 更新時、自分のカラムグループを選択していないかどうか確認
    if parent_column_group and column_group_name and parent_column_group == column_group_name:
        retBool = False
        msg = "自分のカラムグループは親カラムグループに選択できません。"
    if not retBool:
        return retBool, msg, option

    # 親ディレクトリがループ関係かどうかチェック
    table_name = "T_MENU_COLUMN_GROUP"
    if cmd_type == "Update":
        if parent_column_group:
            if entry_uuid:
                uuid = entry_uuid
            else:
                uuid = column_group_name
        where_str = "WHERE CREATE_COL_GROUP_ID = %s"
        
        while True:
            bind_value_list = [parent_column_group]
            return_values = objdbca.table_select(table_name, where_str, bind_value_list)
            if len(return_values) == 0:
                break
            else:
                if uuid == return_values[0].get("PA_COL_GROUP_ID"):
                    retBool = False
                    msg = "ループ関係になるため選択不可です。"
                    break
                elif not return_values[0].get("PA_COL_GROUP_ID"):
                    break
                else:
                    parent_column_group = return_values[0].get("PA_COL_GROUP_ID")
        if not retBool:
            return retBool, msg, option
    # ---------親カラムグループ---------

    # ---------カラムグループ名---------
    # 廃止対象が親になっている場合はエラー
    if cmd_type == "Discard":
        where_str = "WHERE DISUSE_FLAG = '0'"
        return_values = objdbca.table_select(table_name, where_str, [])
        matcharray = []
        for data in return_values:
            if column_group_name == data.get("PA_COL_GROUP_ID"):
                matcharray.append(data.get("CREATE_COL_GROUP_ID"))
        if len(matcharray) > 0:
            retBool = False
            msg = "親カラムグループに選択されているため廃止できません。子カラムグループの項番{}".format(matcharray)
    
    # 復活時、親カラムグループが廃止されていたらエラー
    if cmd_type == "Restore":
        where_str = "WHERE FULL_COL_GROUP_NAME_{} = %s".format(user_env)
        current_parent_column_group = current_parameter.get("parent_column_group")
        bind_value_list = [current_parent_column_group]
        return_values = objdbca.table_select(table_name, where_str, bind_value_list)
        
        if return_values[0].get("DISUSE_FLAG") == "1":
            retBool = False
            msg = "親カラムグループが廃止されています。項番{}".format(return_values[0].get("CREATE_COL_GROUP_ID"))
    # ---------カラムグループ名---------
    
    return retBool, msg, option
