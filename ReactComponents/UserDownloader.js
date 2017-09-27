import React, { Component } from 'react';
import io from 'socket.io/node_modules/socket.io-client';
import PldAuthService from './PldAuthService';
import {Button, Glyphicon, Table, ProgressBar} from 'react-bootstrap';

function OrigenFormatter(props){
  return <img className={`pl-img-${props.value}`}/>
}

class Downloader extends Component {
  constructor(){ super(); this.state={} }
  render(){
    if(!this.props.status){
      return (
        <Button
          bsStyle="link"
          className='pl-button'
          disabled={this.props.disabled}
          onClick={this.props.clickHandler}>
          <Glyphicon glyph="save"/>
        </Button>)
    }
    else if(this.props.status == "finished"){
      return <a href={this.props.auth.getdownloadUrl(this.props.uuid)}>Descargar</a>
    }
    else return <ProgressBar className="pld-progress-bar" now={100 * this.props.c / this.props.t } />
  }
}

class Updater extends Component {
  constructor(){super(); this.state={}}
  updatePlaylist(){
    let {source, id, url} = this.props
    let config = {source: source, id: id, url: url}
    this.props.showLoading()
    this.props.auth.updatePlaylist(config).then(res=>{
      this.props.hideLoading()
      this.props.updateTotalMissing(id, res.data)
    })
  }
  render(){
    return (<Button
      bsStyle="link"
      className='pl-button'
      onClick={this.updatePlaylist.bind(this)}>
      <Glyphicon glyph="refresh"/>
    </Button>)
  }
}

class PlaylistRow extends Component {
  constructor(props){super(props); this.state={downloading: false}}
  handleFullDownload(){
    this.setState({downloading: true})
    this.props.auth.downloadFull(this.props.id)
  }
  handlePartialDownload(){
    this.setState({downloading: true})
    this.props.auth.downloadPartial(this.props.id)
  }
  handleRemove(){
    this.props.auth.unlinkPlaylist(this.props.id).then(res => {
      this.props.removePlaylist(this.props.id)
    })
  }
  render(){
    return(<tr className='pl-table-row'>
        <td className='pl-table-td'><Updater {...this.props}/></td>
        <td className='pl-table-td'><OrigenFormatter value={this.props.source}/></td>
        <td className='pl-table-td'><a className='pl-name' href={this.props.url} target="_blank">{this.props.name}</a></td>
        <td className='pl-table-td'>{this.props.total}</td>
        <td className='pl-table-td'>{this.props.missing}</td>
        <td className='pl-table-td'><Downloader clickHandler={this.handleFullDownload.bind(this)} disabled={this.state.downloading} {...this.props}/></td>
        <td className='pl-table-td'><Downloader clickHandler={this.handlePartialDownload.bind(this)} disabled={this.state.downloading} {...this.props}/></td>
        <td className='pl-table-td'><Button onClick={this.handleRemove.bind(this)} disabled={this.state.downloading} bsStyle="link" className='pl-button delete-btn'><Glyphicon glyph="remove"/></Button></td>
      </tr>)
  }
}

class PlaylistsTable extends Component {
  constructor(props){super(props);}
  render(){
    let rows = this.props.playlists && this.props.playlists.map((obj,i) => <PlaylistRow
        key={i}
        {...this.props}
        {...obj}/>)
    if(rows && rows.length == 0){ rows = (<tr><td colSpan="8">No playlists</td></tr>) }
    return(<Table responsive id='playliststable'>
    <thead>
      <tr>
        <th className='pl-table-header'></th>
        <th className='pl-table-header'></th>
        <th className='pl-table-header'>Title</th>
        <th className='pl-table-header'>Total</th>
        <th className='pl-table-header'>Not downloaded</th>
        <th className='pl-table-header'>Download all</th>
        <th className='pl-table-header'>Download new</th>
        <th className='pl-table-header'>Delete</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </Table>)
  }
}

class UserDownloader extends Component {
  constructor(props){
    super(props);
    this.state = {
      inputUrl: '',
      playlists: [],
      loading: false
    }
  }
  componentDidMount(){
    let _this = this,
        userId = this.props.auth.getUserId(),
        socket = io.connect('http://localhost:5000');

    // Cargar las playlists
    this.props.auth.getPlaylists().then(res =>{
      _this.setState({playlists: res.data})
    })

    // WebSocket Listener
    socket.on(`${userId}`, data => {
      let playlists = _this.state.playlists;
      playlists.forEach((p, i) => {
        if(p.id == data.playlist_id){
          playlists[i] = Object.assign({}, p, data)
        }
      })
      _this.setState({playlists: playlists})
    });
  }
  inputOnChange(e){ this.setState({inputUrl: e.target.value}) }
  showLoading(){this.setState({loading: true})}
  hideLoading(){this.setState({loading:false})}
  removePlaylist(id){
    let {playlists} = this.state;
    this.setState({playlists: playlists.filter(p => p.id != id)})
  }
  updateTotalMissing(id, data){
    let playlists = this.state.playlists;
    let i = playlists.findIndex(p => p.id==id);
    playlists[i] = Object.assign({}, playlists[i], data);
    this.setState({playlists: playlists});
  }
  handleClick(){
    let _this = this;
    if (/youtube.com\/playlist\?list=.*|spotify.com\/user\/\d+|.+\/playlist\/.*|user:[^:]+:playlist:.*|soundcloud.com.*/.test(this.state.inputUrl)){
      let config = {url: this.state.inputUrl}
      this.showLoading()
      this.props.auth.registerPlaylist(config).then(res=>{
        this.hideLoading()
        if(res.data){
          _this.setState({playlists: _this.state.playlists.concat(res.data), inputUrl: ''})
        }
      })
    }
    else{alert('URL no valida')}
  }
  render(){
    return(<div>
        <h3>Add new playlist:</h3>
        <input
          type="text"
          placeholder="Url"
          className="mc-input bottom-border"
          onChange={this.inputOnChange.bind(this)}
          value={this.state.inputUrl}
          />
        <Button
          bsStyle="primary"
          className='mc-button inline-button'
          onClick={this.handleClick.bind(this)}>
          <Glyphicon glyph="plus"/> Add</Button>
        <PlaylistsTable
          playlists={this.state.playlists}
          removePlaylist={this.removePlaylist.bind(this)}
          updateTotalMissing={this.updateTotalMissing.bind(this)}
          showLoading={this.showLoading.bind(this)}
          hideLoading={this.hideLoading.bind(this)}
          auth={this.props.auth}/>
        {this.state.loading ? <div className='body-loading'></div> : null}
      </div>)
  }
}

export default UserDownloader