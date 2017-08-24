import models as m
from sqlalchemy import or_, and_
import utils.pwsecurity as PWS

def valid_name(name):
    """ Checa que no existan usuarios con name """
    u = m.s.query(m.User).filter(m.User.name == name).first()
    if u is None:
        return True
    return False

def valid(attr, name):
    """ Checa que no existan usuarios con email """
    u = m.s.query(m.User).filter(getattr(m.User, attr) == name).first()
    if u is None:
        return True
    return False

def create_user(user={}):
    """ Añade un nuevo usuario """
    m.s.add(m.User(**user))
    m.s.commit()
    return True

def change_password(user_id, password):
    """ Se cambia el password, ya debe venir hasheado """
    m.s.query(m.User).filter(m.User.id == user_id).update({
        m.User.password: password
    })
    m.s.commit()

def change_permissions(user_id, permissions):
    """ Editar los permisos anteriores """
    m.s.query(m.User).filter(m.User.id == user_id).update({
        m.User.permissions: permissions
    })
    m.s.commit()

def delete_user(user_id):
    """ Elimina primero las relaciones user-playlist y luego al user """
    m.s.query().filter()
    m.s.commit()

def valid_password(password, name):
    """ Usado en login """
    user = m.s.query(m.User).filter(or_(m.User.email == name, m.User.name == name)).first()
    if PWS.check(plain_text_password=password, hashed_password=user.password):
        return user.id
    return False

def get_playlists(user_id):
    """
    Informacion basica de las playlists de un usuario.

    Falta incluir last_date y last_type
    """
    playlists = m.s.query(m.User).filter_by(id=user_id).first().playlists
    return [{
        'id': p.id,
        'url': p.url,
        'name': p.name,
        'source': p.source,
        'total': len(p.songs),
        'missing': len(p.songs) - m.s.query(
            m.Downloaded.song_id).filter(and_(
                m.Downloaded.user_id == user_id,
                m.Downloaded.playlist_id == p.id
            )).count()
    } for p in playlists]

def get_basic_info(user_id):
    user = m.s.query(m.User).filter_by(id=user_id).first()
    if user is None:
        return False
    return {
        'name': user.name,
        'id': user.id,
    }
