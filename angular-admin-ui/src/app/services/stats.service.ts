import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http } from '@angular/http'

import { Stat } from '../models/stat'

@Injectable()
export class StatsService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private configUrl = '/stats';

  constructor(private http: Http) {}

  getStats(): Promise<Stat> {
    const url = `${this.configUrl}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as Stat)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (Config Stat)', error);
    return Promise.reject(error.message || error);
  }
}
