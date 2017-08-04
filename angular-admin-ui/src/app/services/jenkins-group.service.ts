import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions, URLSearchParams } from '@angular/http'

import { JenkinsGroup } from '../models/jenkins-group'

@Injectable()
export class JenkinsGroupService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private delayedTaskUrl = '/admin/api/v1/jenkins-group';

  constructor(private http: Http) {}

  getJenkinsGroup(id: number): Promise<JenkinsGroup> {
    const url = `${this.delayedTaskUrl}/${id}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as JenkinsGroup)
      .catch(this.handleError);
  }

  searchJenkinsGroups(name: string): Promise<JenkinsGroup[]> {
    const url = `${this.delayedTaskUrl}`;

    let params: URLSearchParams = new URLSearchParams();
    params.set("name", name);

    return this.http.get(url, {search: params})
      .toPromise()
      .then(response => response.json() as JenkinsGroup[])
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (JenkinsGroup API)', error);
    return Promise.reject(error.message || error);
  }
}
