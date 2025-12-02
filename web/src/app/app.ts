import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { TopBanner } from './top-banner/top-banner';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TopBanner],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    'class': 'block min-h-screen w-full'
  }
})
export class App {
  protected readonly title = signal('web');
}
