import React, { Component } from "react";
import MainComponent from "./MainComponent";
import PldAuthService from "./PldAuthService";
import HeaderComponent from './HeaderComponent';

 class App extends Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {  }

  render() {
    return (
      <div>
        <HeaderComponent auth={this.props.auth}/>
        <MainComponent auth={this.props.auth}/>
      </div>
    );
  }
}


App.defaultProps = {
  auth: new PldAuthService()
}

export default App;