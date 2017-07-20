import React, { Component } from 'react';
import io from 'socket.io/node_modules/socket.io-client';
import {Button, Glyphicon, Table} from 'react-bootstrap';

class AnonDownloader extends Component {
  constructor(props){
    super(props);
    this.state = {
      inputUrl: ''
    }
  }
  handleClick(){}
  render(){
    return(<div>
        <h3>Enter your playlist URL:</h3>
        <input
          type="text"
          placeholder="Url"
          className="mc-input"
          onChange={e => this.setState({inputUrl:e.target.value})}
          value={this.state.inputUrl}
          />
        <Button
          bsStyle="primary"
          className='mc-button'
          onClick={this.handleClick.bind(this)}
          style={{marginTop: 20}}>
          <Glyphicon glyph="download-alt"/> Download</Button>
      </div>)
  }
}
export default AnonDownloader;