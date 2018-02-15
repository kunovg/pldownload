import React, { Component } from 'react';
import {Button, Table} from 'react-bootstrap';
import FaDownload from 'react-icons/lib/fa/download';

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
          <FaDownload /> Download</Button>
      </div>)
  }
}
export default AnonDownloader;