import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions, URLSearchParams } from '@angular/http'

import { JenkinsJob } from '../models/jenkins-job'

@Injectable()
export class JenkinsJobService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private jenkinsJobUrl = '/api/admin/v1/jenkins-job';

  constructor(private http: Http) {}

  getJenkinsJobs(groupId: number): Promise<JenkinsJob[]> {
    const url = `${this.jenkinsJobUrl}/${groupId}`;

    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as JenkinsJob[])
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (JenkinsJob API)', error);
    return Promise.reject(error.message || error);
  }
}
