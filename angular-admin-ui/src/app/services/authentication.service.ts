import { Injectable } from '@angular/core';
import { Http, Headers, Response, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map'

@Injectable()
export class AuthenticationService {
  private headers = new Headers({'Content-Type': 'application/json'});

  constructor(private http: Http) { }

  login(username: string, password: string) {
    return this.http.post('/api/v1/login', JSON.stringify({ username: username, password: password }))
      .map((response: Response) => {
          let user = response.json();
          if (user && user.username) {
            //TODO: need implement jwt token
            localStorage.setItem('currentUser', JSON.stringify(user.username));
          }
      });
  }

  logout() {
    localStorage.removeItem('currentUser');
    this.http.delete('/api/v1/logout', new RequestOptions({ headers: this.headers }))
       .subscribe(res => { console.log('Logout');});
  }
}
