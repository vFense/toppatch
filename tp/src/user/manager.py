
import logging
import logging.config
from models.account import *
from models.user_acl import *
from server.oauth import token

from utils.security import Crypto
from db.client import validate_session
from db.update_table import *
from utils.common import *


logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')


def list_user(session):
    session = validate_session(session)
    userlist = session.query(User).all()
    user_dict = {}
    user_groups = map(lambda x: (x[0].user_id, x[1].groupname), 
            session.query(UsersInAGroup, Group).join(Group).all())
    for i in user_groups:
        if str(i[0]) in user_dict:
            user_dict[str(i[0])].append(i[1])
        else:
            user_dict[str(i[0])] = [i[1]]
    node_acl_list =[]
    tag_acl_list = []
    global_acl_list = []
    result = []
    for user in userlist:
        if not str(user.id) in user_dict:
            user_dict[str(user.id)] = []
        node_user_acl = session.query(NodeUserAccess).\
                filter(NodeUserAccess.user_id == user.id).\
                all()
        node_acl_list = map(lambda node: node.__dict__, node_user_acl)
        map(lambda node: node.pop('_sa_instance_state'), node_acl_list)
        global_user_acl = session.query(GlobalUserAccess).\
                filter(GlobalUserAccess.user_id == user.id).\
                all()
        global_acl_list = map(lambda user: user.__dict__, global_user_acl)
        map(lambda user: user.pop('_sa_instance_state'), global_acl_list)
        map(lambda node: node.pop('is_global'), global_acl_list)
        tag_user_acl = session.query(TagUserAccess).\
                filter(TagUserAccess.user_id == user.id).\
                all()
        tag_acl_list = map(lambda tag: tag.__dict__, tag_user_acl)
        map(lambda tag: tag.pop('_sa_instance_state'), tag_acl_list)
        result.append({
            'username': user.username,
            'id': user.id,
            'groups': user_dict[str(user.id)],
            'global_acls': return_modified_list(global_acl_list),
            'node_acls': return_modified_list(node_acl_list),
            'tag_acls': return_modified_list(tag_acl_list)
            })
    return result

def create_user(session, username=None, password=None,
        fullname=None, email=None, groupname='READ_ONLY',
        user_name=None):
    session = validate_session(session)
    if username and password and groupname:
        user_exists = session.query(User).\
                filter(User.username == username).first()
        if not user_exists:
            user = None
            user_hash = Crypto.hash_scrypt(password)
            try:
                user = User(username, user_hash, fullname, email)
                session.add(user)
                session.commit()
                group = session.query(Group).\
                        filter(Group.groupname == groupname).first()
                if group:
                    user_to_group = \
                            add_user_to_group(session, user_id=user.id,
                                    group_id=group.id)
                    if user_to_group['pass'] == True:
                        return({
                            'pass': True,
                            'message': \
                                    'User %s was created and added to group %s'%\
                                    (username, groupname)
                            })
                    else:
                        return({
                            'pass': False,
                            'message': \
                                    'User %s was created and not added to group %s'%\
                                    (username, groupname)
                            })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'User %s was not created and added to group %s'%\
                            (username, groupname)
                    })
        else:
            return({
                    'pass': False,
                    'message': 'User %s already exists'%\
                        (username)
                    })

def delete_user(session, user_id, username='system_user'):
    session = validate_session(session)
    result = None
    if user_id:
        user = session.query(User).\
                filter(User.id == user_id).first()
        if user:
            global_acl = session.query(GlobalUserAccess).\
                    filter(GlobalUserAccess.user_id == user.id).first()
            node_acl = session.query(NodeUserAccess).\
                    filter(NodeUserAccess.user_id == user.id).all()
            tag_acl = session.query(TagUserAccess).\
                    filter(TagUserAccess.user_id == user.id).all()
            user_in_groups = session.query(UsersInAGroup).\
                    filter(UsersInAGroup.user_id == user.id).all()
            try:
                if user.id != 1:
                    if global_acl:
                        session.delete(global_acl)
                    if len(node_acl) >= 1:
                        map(lambda nodeacl: session.delete(nodeacl),\
                                node_acl)
                    if len(tag_acl) >= 1:
                        map(lambda tagacl: session.delete(tagacl),\
                                tag_acl)
                    if len(user_in_groups) >= 1:
                        map(lambda user_group: session.delete(user_group),\
                                user_in_groups)
                    session.commit()
                    session.delete(user)
                    session.commit()
                    logger.info('%s - user %s has been deleted'%\
                            (username, user.username)
                           ) 
                    result = {"pass" : True,
                              "message" : "%s user deleted" % \
                                              (user.username)
                             }
                else:
                    logger.info('%s - user %s could not be deleted'%\
                            (username, user.username)
                           ) 
                    result = {"pass" : False,
                              "message" : "%s user could not be deleted" % \
                                              (user.username)
                             }
            except Exception as e:
                session.rollback()
                logger.info('%s - user %s could not be deleted, message:%s'%\
                        (username, user.username, e)
                        ) 
                result = {"pass" : False,
                          "message" : "%s user could not be deleted" % \
                                          (user.username)
                         }
        else:
            result = {"pass" : False,
                      "message" : "%s user does not exist" % \
                                     (user.username)
                         }
    return result


def modify_user_from_group(session, user_id=None, group_id=None, action=None):
    session = validate_session(session)
    if user_id and group_id and action:
        user = session.query(UsersInAGroup).\
                filter(UsersInAGroup.user_id == user_id).\
                filter(UsersInAGroup.group_id == group_id).first()
        user1 = session.query(User).filter(User.id == user_id).first()
        group = session.query(Group).filter(Group.id == group_id).first()
        if user and group and 'remove' in action:
            try:
                session.delete(user)
                session.commit()
                return({
                    'pass': True,
                    'message': 'User %s has been removed from Group %s' %\
                            (user1.username, group.groupname)
                            })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'User %s couldnt be removed from the Group %s' %\
                            (user1.username, group.groupname)
                            })
        elif not user and group and 'add' in action:
            try:
                user = session.query(User).filter(User.id == user_id).first()
                addtogroup = UsersInAGroup(user_id, group_id)
                session.add(addtogroup)
                session.commit()
                return({
                    'pass': True,
                    'message': 'User %s has been added to Group %s' %\
                            (user.username, group.groupname)
                            })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'User %s couldnt be added to the Group %s' %\
                            (user.username, group.groupname)
                            })
        else:
            return({
                'pass': False,
                'message': 'User %s and or Group %s do not exist' %\
                        (user_id, group_id)
                        })
    else:
        return({
            'pass': False,
            'message': 'Incorrect parameters were passed'
            })


def list_groups(session):
    session = validate_session(session)
    grouplist = session.query(Group).all()
    node_acl_list =[]
    tag_acl_list = []
    global_acl_list = []
    result = []
    for group in grouplist:
        node_group_acl = session.query(NodeGroupAccess).\
                filter(NodeGroupAccess.group_id == group.id).\
                all()
        node_acl_list = map(lambda node: node.__dict__, node_group_acl)
        map(lambda node: node.pop('_sa_instance_state'), node_acl_list)
        global_group_acl = session.query(GlobalGroupAccess).\
                filter(GlobalGroupAccess.group_id == group.id).\
                all()
        global_acl_list = map(lambda groups: groups.__dict__, global_group_acl)
        map(lambda groups: groups.pop('_sa_instance_state'), global_acl_list)
        map(lambda node: node.pop('is_global'), global_acl_list)
        tag_group_acl = session.query(TagGroupAccess).\
                filter(TagGroupAccess.group_id == group.id).\
                all()
        tag_acl_list = map(lambda tag: tag.__dict__, tag_group_acl)
        map(lambda tag: tag.pop('_sa_instance_state'), tag_acl_list)
        result.append({
            'groupname': group.groupname,
            'id': group.id,
            'global_acls': return_modified_list(global_acl_list),
            'node_acls': return_modified_list(node_acl_list),
            'tag_acls': return_modified_list(tag_acl_list)
            })
    return result


def create_group(session, groupname):
    session = validate_session(session)
    result = None
    if groupname:
        result = add_group(session, groupname)
        return(result)
    else:
        return({
            'pass': False,
            'message': 'Need to pass the groupname'
            })

def delete_group(session, group_id=None, username='system_user'):
    session = validate_session(session)
    if group_id:
        if int(group_id) >=5:
            group = session.query(Group).\
                    filter(Group.id == group_id).first()
            if group:
                global_acl = session.query(GlobalGroupAccess).\
                        filter(GlobalGroupAccess.group_id == group_id).first()
                tag_acl = session.query(TagGroupAccess).\
                        filter(TagGroupAccess.group_id == group_id).all()
                node_acl = session.query(NodeGroupAccess).\
                        filter(NodeGroupAccess.group_id == group_id).all()
                user_in_groups = session.query(UsersInAGroup).\
                        filter(UsersInAGroup.group_id == group.id).all()
                try:
                    if global_acl:
                        session.delete(global_acl)
                    if len(node_acl) >= 1:
                        map(lambda nodeacl: session.delete(nodeacl),\
                                node_acl)
                    if len(tag_acl) >= 1:
                        map(lambda tagacl: session.delete(tagacl),\
                                tag_acl)
                    if len(user_in_groups) >= 1:
                        map(lambda user_group: session.delete(user_group),\
                                user_in_groups)
                    session.commit()
                    session.delete(group)
                    session.commit()
                    logger.info('%s - user %s has been deleted'%\
                            (username, group.groupname)
                            ) 
                    result = {
                            "pass" : True,
                            "message" : "%s group deleted" % \
                                    (group.groupname)
                             }
                except Exception as e:
                    session.rollback()
                    result = {
                            "pass" : False,
                            "message" : "%s group couldnt be deleted %s" % \
                                    (group.groupname, e)
                            }
            else:
                 logger.info('%s - %s group doesnt exist'%\
                       (username, group_id)
                       ) 
                 result = {
                     "pass" : False,
                     "message" : "%s group doesnt exist" % \
                             (group_id)
                    }
        else:
            logger.info('%s - %s Cant delete default groups'%\
                   (username, group_id)
                   ) 
            result = {"pass" : False,
                      "message" : "%s Cant delete default groups" % \
                              (group_id)
                    }
    else:
        logger.info('%s - Need to pass the groupid'%\
              (username)
              ) 
        result = {
                'pass': False,
                'message': 'Need to pass the groupid'
                }
    return result

def acl_modifier(session, acl_type, acl_action, acl):
    session = validate_session(session)
    valid_acl_type = ['global_user', 'global_group', 'node_user', \
            'node_group', 'tag_user', 'tag_group']
    valid_acl_action = ['create', 'modify', 'delete']
    result = None
    if acl_type and acl_action and acl:
        if acl_type in valid_acl_type and \
                acl_action in \
                valid_acl_action:
            for key, value in acl.items():
                if value == 'true'  or value == 'false':
                    acl[key] = return_bool(value)
            if acl_action == 'create':
                if 'global_user' in acl_type:
                    result = add_global_user_acl(session, **acl)
                if 'global_group' in acl_type:
                    result = add_global_group_acl(session, **acl)
                if 'node_user' in acl_type:
                    result = add_node_user_acl(session, **acl)
                if 'node_group' in acl_type:
                    result = add_node_group_acl(session, **acl)
                if 'tag_user' in acl_type:
                    result = add_tag_user_acl(session, **acl)
                if 'tag_group' in acl_type:
                    result = add_tag_group_acl(session, **acl)
            elif acl_action == 'modify':
                if 'global_user' in acl_type:
                    result = update_global_user_acl(session, **acl)
                if 'global_group' in acl_type:
                    result = update_global_group_acl(session, **acl)
                if 'node_user' in acl_type:
                    result = update_node_user_acl(session, **acl)
                if 'node_group' in acl_type:
                    result = update_node_group_acl(session, **acl)
                if 'tag_user' in acl_type:
                    result = update_tag_user_acl(session, **acl)
                if 'tag_group' in acl_type:
                    result = update_tag_group_acl(session, **acl)
            elif acl_action == 'delete':
                result = remove_acl(session, acl_type, **acl)
        else:
            result({
                'pass': False,
                'message': 'the acl_type or acl_action was invalid'
                })
    else:
        result({
            'pass': False,
            'message': 'Arguments needed are acl_type, acl_action, and acl'
            })
    return result
