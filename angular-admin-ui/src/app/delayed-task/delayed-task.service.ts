import { Injectable } from '@angular/core';
import { Headers, Http } from '@angular/http'

import 'rxjs/add/operator/toPromise';

import { DelayedTask } from './delayed-task'

@Injectable()
export class DelayedTaskService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private configUrl = '/admin/api/v1/delayed-task';

  constructor(private http: Http) {}

  getDelayedTasks(): Promise<DelayedTask[]> {
    const url = `${this.configUrl}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as DelayedTask[])
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (Config API)', error);
    return Promise.reject(error.message || error);
  }
}
