import axios from 'axios';
import { EventEmitter } from 'events';
import jwtDecode from 'jwt-decode';

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
  getAccessT(){ return localStorage.getItem('access_token'); }
  loggedIn(){ return localStorage.getItem('loggedIn'); }
  getName(){ return jwtDecode(this.getAccessT()).user_claims.name; }
  getUserId(){ return jwtDecode(this.getAccessT()).user_claims.id; }
  /**
  * Login
  * @param {Object} data - {user, password}
  * @return {Object} User profile
  */
  login(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/login',
      data: data,
    })
  }
  /**
  * Logout
  */
  logout(){
    localStorage.removeItem('loggedIn');
    localStorage.removeItem('access_token');
    this.emit('reload');
  }
  /**
  * Checks if email or username is available
  * @param {Object} data - {attr: value}
  * @return {Boolean} Available or not
  */
  validate(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/validate',
      data: data,
    });
  }
  /**
  * All of a user playlists
  * @return {Array} list of objects with playlists information
  */
  getPlaylists(){
    return axios({
      method: 'get',
      url: `http://localhost:5000/playlists?userId=${this.getUserId()}`,
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Register new user
  * @param {Object} data - {name, email, password}
  * @return {Boolean} Always True, or 500 status
  */
  registerUser(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/user/create',
      data: data,
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Update songs in a Playlist
  * @param {Object} data - {source, id, url}
  * @return {Object} {total, missing}
  */
  updatePlaylist(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/playlist/update',
      data: data,
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Unlink a playlist from a user
  * @param {Integer} playlistId
  * @return {Object} {bool}
  */
  unlinkPlaylist(playlistId){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/playlist/unlink',
      data: {id: playlistId},
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Read a new playlist
  * @param {Object} data - {url}
  * @return {Object} {id, url, name, source, total, missing}
  */
  registerPlaylist(data){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/playlist/create',
      data: data,
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Request to start a full download of playlist
  * @param {Integer} playlistId
  * @return {Object} {success}
  */
  downloadFull(playlistId){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/fulldownload',
      data: {playlistId: playlistId},
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Request to start a partial download of playlist
  * @param {Integer} playlistId
  * @return {Object} {success}
  */
  downloadPartial(playlistId){
    return axios({
      method: 'post',
      url: 'http://localhost:5000/partialdownload',
      data: {playlistId: playlistId},
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
  /**
  * Request to start check if current token is valid
  */
  validToken(){
    return axios({
      method: 'get',
      url: 'http://localhost:5000/valid_token',
      headers: {Authorization: `Bearer ${this.getAccessT()}`}
    });
  }
}