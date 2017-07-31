import axios from 'axios';
import { EventEmitter } from 'events';

/********************
De esta clase se obtiene toda la información del servidor
Falta:
-checar que el usuario esté activo
********************/
export default class PldAuthService extends EventEmitter{
  constructor(props, context){
    super(props, context);
    this.on('reload', () => { location.reload(true) });
    this.on('loginFail', () => { alert('Error de usuario y contraseña') });
  }
  getdownloadUrl(uuid){ return `http://localhost:5000/get?uuid=${uuid}` }
  getName(){return localStorage.profile ? JSON.parse(localStorage.profile).name : null}
  getUserId(){return localStorage.profile ? JSON.parse(localStorage.profile).id : null}
  loggedIn(){ return localStorage.getItem('loggedIn'); }
  login(data){
    let _this = this;
    axios({
      method: 'post',
      url: 'http://localhost:5000/login',
      data: data,
    })
      .then(res => {
        localStorage.setItem('loggedIn', true);
        localStorage.setItem('profile', JSON.stringify(res.data));
        _this.emit('reload')
      })
      .catch(err => {_this.emit('loginFail')});
  }
  logout(){
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('profile');
    this.emit('reload');
  }
  getPlaylists(){
    return axios({
      method: 'get',
      url: `http://localhost:5000/playlists?userId=${this.getUserId()}`,
    });
  }
  validate(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/validate',
      data: data,
    });
  }
  registerUser(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/user/create',
      data: data,
      headers: {User: `${this.getUserId()}`}
    });
  }
  registerPlaylist(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/playlist/create',
      data: data,
      headers: {User: `${this.getUserId()}`}
    });
  }
  downloadFull(playlistId){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/fulldownload',
      data: {playlistId: playlistId},
      headers: {User: `${this.getUserId()}`}
    });
  }
}