// TypeScript Web 3D Visualization Adapter
import { Point3D } from '../spatial_core/models';

export interface ViewerOptions {
  canvasId: string;
  fps: number;
  enableAntiAliasing: boolean;
}

export class PoseViewer {
  private canvasId: string;
  private isRunning: boolean;

  constructor(options: ViewerOptions) {
    this.canvasId = options.canvasId;
    this.isRunning = false;
  }

  public startRenderLoop(): void {
    this.isRunning = true;
    console.log(`Starting render loop on ${this.canvasId}`);
  }

  public renderAxes(origin: Point3D): boolean {
    if (!this.isRunning) {
      return false;
    }
    // Render X, Y, Z axes
    return true;
  }
}

export function createDefaultViewer(canvasId: string): PoseViewer {
  return new PoseViewer({
    canvasId: canvasId,
    fps: 60,
    enableAntiAliasing: true
  });
}
