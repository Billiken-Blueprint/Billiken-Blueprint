import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TopBanner } from './top-banner/top-banner';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TopBanner],
  templateUrl: './app.html',
  styleUrl: './app.css',
  host: {
    'class': 'block min-h-screen w-full'
  }
})
export class App {
  protected readonly title = signal('web');
}
