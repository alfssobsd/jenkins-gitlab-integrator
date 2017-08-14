import 'rxjs/add/operator/toPromise';
import { Injectable } from '@angular/core';
import { Headers, Http, RequestOptions, URLSearchParams } from '@angular/http'

import { JenkinsJob } from '../models/jenkins-job'

@Injectable()
export class JenkinsJobService {
  private headers = new Headers({'Content-Type': 'application/json'});
  private jenkinsGroupUrl = '/api/admin/v1/jenkins-group';
  private jenkinsJobPartUrl = 'jenkins-job';

  constructor(private http: Http) {}

  getJenkinsJobs(groupId: number): Promise<JenkinsJob[]> {
    const url = `${this.jenkinsGroupUrl}/${groupId}/${this.jenkinsJobPartUrl}`;

    return this.http.get(url)
      .toPromise()
      .then(response => response.json() as JenkinsJob[])
      .catch(this.handleError);
  }

  createJenkinsJob(job: JenkinsJob): Promise<JenkinsJob> {
    const url = `${this.jenkinsGroupUrl}/${job.jenkins_group_id}/${this.jenkinsJobPartUrl}`;

    return this.http.post(url, job, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as JenkinsJob)
      .catch(this.handleError)
  }

  updateJenkinsJob(job: JenkinsJob): Promise<JenkinsJob> {
    const url = `${this.jenkinsGroupUrl}/${job.jenkins_group_id}/${this.jenkinsJobPartUrl}/${job.id}`;

    return this.http.put(url, job, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as JenkinsJob)
      .catch(this.handleError);
  }

  deleteJenkinsJob(job: JenkinsJob): Promise<string> {
    const url = `${this.jenkinsGroupUrl}/${job.jenkins_group_id}/${this.jenkinsJobPartUrl}/${job.id}`;

    return this.http.delete(url, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as string)
      .catch(this.handleError);
  }


  updateJenkinsJobWebHook(job: JenkinsJob) {
    const url = `${this.jenkinsGroupUrl}/${job.jenkins_group_id}/${this.jenkinsJobPartUrl}/${job.id}/hook`;

    return this.http.put(url, job, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as string)
      .catch(this.handleError);
  }

  deleteJenkinsJobWebHook(job: JenkinsJob) {
    const url = `${this.jenkinsGroupUrl}/${job.jenkins_group_id}/${this.jenkinsJobPartUrl}/${job.id}/hook`;

    return this.http.delete(url, new RequestOptions({ headers: this.headers }))
      .toPromise()
      .then(response => response.json() as string)
      .catch(this.handleError);
  }

  private handleError(error: any): Promise<any> {
    console.error('ERROR (JenkinsJob API)', error);
    return Promise.reject(error.message || error);
  }
}
