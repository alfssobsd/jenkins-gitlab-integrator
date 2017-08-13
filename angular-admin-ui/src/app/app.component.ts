import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ToastyConfig } from 'ng2-toasty';

import { Stat }        from './models/stat'
import { StatsService } from './services/stats.service'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent  implements OnInit {
  title = 'jenkins-gitlab-integrator';
  stat: Stat;
  currentPath: string;


  constructor(
    private statsService: StatsService,
    private router: Router,
    private toastyConfig: ToastyConfig
  ) {
    this.toastyConfig.theme = 'bootstrap';
    this.toastyConfig.position = 'top-right';
    this.toastyConfig.timeout = 5000;
    router.events.subscribe((obj:any) => { this.currentPath = obj.url.split('?')[0]});
  }

  ngOnInit() {
    this.statsService
      .getStats()
      .then(stat => this.stat = stat)
  }
}
