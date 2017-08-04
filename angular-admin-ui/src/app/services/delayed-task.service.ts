import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions, URLSearchParams } from '@angular/http'

import { DelayedTask } from '../models/delayed-task'

@Injectable()
export class DelayedTaskService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private delayedTaskUrl = '/admin/api/v1/delayed-task';

  constructor(private http: Http) {}

  getDelayedTasks(): Promise<DelayedTask[]> {
    const url = `${this.delayedTaskUrl}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as DelayedTask[])
      .catch(this.handleError);
  }

  getDelayedTask(id: number): Promise<DelayedTask> {
    const url = `${this.delayedTaskUrl}/${id}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as DelayedTask)
      .catch(this.handleError);
  }

  searchDelayedTasks(searchData: DelayedTask): Promise<DelayedTask[]> {
    const url = `${this.delayedTaskUrl}`;

    let params: URLSearchParams = new URLSearchParams();
    params.set("task_type", searchData.task_type);
    params.set("group", searchData.group);
    params.set("job_name", searchData.job_name);
    params.set("branch", searchData.branch);
    params.set("sha1", searchData.sha1);

    return this.http.get(url, {search: params})
      .toPromise()
      .then(response => response.json() as DelayedTask[])
      .catch(this.handleError);
  }

  setDelayedTaskStatus(id:number, status: string): Promise<DelayedTask> {
    const url = `${this.delayedTaskUrl}/${id}/status`;
    return this.http
      .post(url, JSON.stringify({'task_status': status}), {headers: this.headers})
      .toPromise()
      .then(response => response.json() as DelayedTask)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (DelayedTask API)', error);
    return Promise.reject(error.message || error);
  }
}
