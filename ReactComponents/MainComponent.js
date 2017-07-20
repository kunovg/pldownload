import React, { Component } from 'react';
import UserDownloader from './UserDownloader';
import AnonDownloader from './AnonDownloader';


class MainComponent extends Component {
  constructor(props) {
    super(props);  
  }
  componentDidMount() {  }
  render() {
    return (
      <div className="mc-container">
        <h1>Welcome <span>{this.props.auth.loggedIn() ? this.props.auth.getName() : ''}</span></h1>
        {this.props.auth.loggedIn() ? <UserDownloader auth={this.props.auth} /> : <AnonDownloader />}
      </div>
    );
  }
}

export default MainComponent;