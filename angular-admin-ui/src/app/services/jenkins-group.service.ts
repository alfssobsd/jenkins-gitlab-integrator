import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions, URLSearchParams } from '@angular/http'

import { JenkinsGroup } from '../models/jenkins-group'

@Injectable()
export class JenkinsGroupService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private jenkinsGroupUrl = '/api/admin/v1/jenkins-group';

  constructor(private http: Http) {}

  getJenkinsGroup(id: number): Promise<JenkinsGroup> {
    const url = `${this.jenkinsGroupUrl}/${id}`;
    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as JenkinsGroup)
      .catch(this.handleError);
  }

  searchJenkinsGroups(name: string): Promise<JenkinsGroup[]> {
    const url = `${this.jenkinsGroupUrl}`;

    let params: URLSearchParams = new URLSearchParams();
    params.set("name", name);

    return this.http.get(url, {search: params})
      .toPromise()
      .then(response => response.json() as JenkinsGroup[])
      .catch(this.handleError);
  }

  createJenkinsGroup(group: JenkinsGroup): Promise<JenkinsGroup> {
    const url = `${this.jenkinsGroupUrl}`;

    return this.http.post(url, group, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as JenkinsGroup)
      .catch(this.handleError)
  }

  updateJenkinsGroup(id:number, group: JenkinsGroup): Promise<JenkinsGroup> {
    const url = `${this.jenkinsGroupUrl}/${id}`;

    return this.http.put(url, group, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as JenkinsGroup)
      .catch(this.handleError);
  }

  deleteJenkinsGroup(id: number): Promise<string> {
    const url = `${this.jenkinsGroupUrl}/${id}`;
    return this.http.delete(url, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as string)
      .catch(this.handleError);
  }

  updateJenkinsGroupWebhooks(id:number): Promise<string> {
    const url = `${this.jenkinsGroupUrl}/${id}/hooks`;
    return this.http.put(url, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as string)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (JenkinsGroup API)', error);
    return Promise.reject(error.message || error);
  }
}
