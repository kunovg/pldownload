import React, { Component } from 'react';
import PldAuthService from './PldAuthService';
import {Button, Glyphicon} from 'react-bootstrap';

class LoginForm extends Component{
  constructor(props){super(props);this.state={loading: false}}
  onBlur(e){
    var currentTarget = e.currentTarget, _this = this;
    setTimeout(() => {
      if (!currentTarget.contains(document.activeElement)) {
        _this.props.hide()
      }
    }, 0);
  }
  handleLogin(){
    this.setState({loading:true});
    setTimeout(()=>{ this.setState({loading:false}); }, 1000);
    this.props.auth.login(this.state);
  }
  handleKeyDown(e){if(e.key=='Enter') this.handleLogin()}
  render(){
    return(
      <div id='loginForm' onBlur={this.onBlur.bind(this)}>
        <input
          autoFocus
          type="text"
          className="hc-input"
          placeholder="user"
          onKeyDown={this.handleKeyDown.bind(this)}
          onChange={(e)=>{this.setState({name:e.target.value})}}
          />
        <input
          type="password"
          className="hc-input"
          placeholder="password"
          onKeyDown={this.handleKeyDown.bind(this)}
          onChange={(e)=>{this.setState({password:e.target.value})}}
          />
        <Button
          className='hc-button header-form-button'
          onClick={this.handleLogin.bind(this)}>
          Log in
        </Button>
        {this.state.loading ? <div className='header-loading'></div> : null}
      </div>
      );
  }
}

class RegisterForm extends Component{
  constructor(props){super(props);this.state={loading: false}}
  onBlurForm(e){
    let currentTarget = e.currentTarget, _this = this;
    setTimeout(() => {
      if (!currentTarget.contains(document.activeElement)) {
        _this.props.hide()
      }
    }, 0);
  }
  handleKeyDown(e){if(e.key=='Enter') this.handleRegister()}
  handleEmailValidation(){
    let _this = this, re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if(re.test(this.state.email )){
      console.log('handleEmailValidation')
      this.props.auth.validate({email:this.state.email})
        .then( res => {
          _this.setState({validEmail: res.data})
        });
    }
  }
  handleNameValidation(){
    let _this = this;
    if (!this.state.name) return true;
    this.props.auth.validate({name:this.state.name})
      .then( res => { _this.setState({validName: res.data}) });
  }
  handlePasswordValidation(e){
    this.setState({password:e.target.value, validPassword: e.target.value.length > 8});
  }
  handlePasswordConfirmation(e){
    this.setState({_password:e.target.value, validPassword2: this.state.password == e.target.value})
  }
  handleRegister(){
    let _this = this;
    if(this.state.validEmail && this.state.validName && this.state.validPassword && this.state.validPassword2)
      this.setState({loading:true});
      this.props.auth.registerUser({name: this.state.name, email: this.state.email, password:this.state.password}).then(()=>{
        _this.props.auth.login({name: _this.state.name, password: _this.state.password})
      })
  }
  render(){
    return(
      <div id='registerForm' onBlur={this.onBlurForm.bind(this)}>
        <input
          autoFocus
          type="text"
          placeholder="email"
          value={this.state.email}
          onKeyDown={this.handleKeyDown.bind(this)}
          className={`hc-input ${this.state.email ? (this.state.validEmail ? 'valid-input' : 'invalid-input') : ''}`}
          onBlur={this.handleEmailValidation.bind(this)}
          onChange={(e)=>{this.setState({email:e.target.value})}}/>
        <input
          type="text"
          placeholder="username"
          onKeyDown={this.handleKeyDown.bind(this)}
          className={`hc-input ${this.state.name ? (this.state.validName ? 'valid-input' : 'invalid-input') : ''}`}
          onBlur={this.handleNameValidation.bind(this)}
          onChange={(e)=>{this.setState({name:e.target.value})}}/>
        <input
          type="password"
          placeholder="password"
          onKeyDown={this.handleKeyDown.bind(this)}
          className={`hc-input ${this.state.password ? (this.state.validPassword ? 'valid-input' : 'invalid-input') : ''}`}
          onChange={this.handlePasswordValidation.bind(this)}/>
        <input
          type="password"
          placeholder="password (again)"
          onKeyDown={this.handleKeyDown.bind(this)}
          className={`hc-input ${this.state._password ? (this.state.validPassword2 ? 'valid-input' : 'invalid-input') : ''}`}
          onChange={this.handlePasswordConfirmation.bind(this)}/>
        <Button
          className='hc-button header-form-button'
          onClick={this.handleRegister.bind(this)}>
          Register
        </Button>
        {this.state.loading ? <div className='header-loading'></div> : null}
      </div>
      );
  }
}

class HeaderComponent extends Component {
  constructor(props) {super(props);this.state={}}
  render() {
    let loginButton, registerButton, logoutButton;
    loginButton = (<Button
      bsStyle="link"
      className='hc-button login-button'
      onClick={() => this.setState({displayLogin: true})}>Login <Glyphicon glyph="log-in"/>
    </Button>)
    registerButton = (<Button
      bsStyle="link"
      className='hc-button register-button'
      onClick={() => this.setState({displayRegister: true})}>Register</Button>)
    logoutButton = (<Button
      bsStyle="link"
      className='hc-button login-button'
      onClick={() => this.props.auth.logout()}>Logout <Glyphicon glyph="log-out"/>
    </Button>);

    return (
      <div className="hc-container">
          {this.props.auth.loggedIn() ? null : registerButton}
          {this.props.auth.loggedIn() ? null : loginButton}
          {this.props.auth.loggedIn() ? logoutButton : null}
          {this.state.displayLogin ? <LoginForm auth={this.props.auth} hide={() => this.setState({displayLogin: false})} /> : null}
          {this.state.displayRegister ? <RegisterForm auth={this.props.auth} hide={() => this.setState({displayRegister: false})} /> : null}
      </div>
    );
  }
}

export default HeaderComponent;