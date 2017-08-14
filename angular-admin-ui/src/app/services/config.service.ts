import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http } from '@angular/http'

import { Config } from '../models/config'

@Injectable()
export class ConfigService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private configUrl = '/api/admin/v1/config';

  constructor(private http: Http) {}

  getConfig(): Promise<Config> {
    const url = `${this.configUrl}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as Config)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (Config API)', error);
    return Promise.reject(error.message || error);
  }
}
