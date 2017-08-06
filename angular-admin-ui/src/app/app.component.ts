import { Component, OnInit } from '@angular/core';

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


  constructor(
    private statsService: StatsService
  ) { }

  ngOnInit() {
    this.statsService
      .getStats()
      .then(stat => this.stat = stat)
  }
}
