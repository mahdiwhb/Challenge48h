declare module 'react-plotly.js' {
  import { Component } from 'react';
  
  interface PlotParams {
    data: any[];
    layout?: any;
    config?: any;
    style?: React.CSSProperties;
    className?: string;
    onHover?: (event: any) => void;
    onClick?: (event: any) => void;
  }
  
  class Plot extends Component<PlotParams> {}
  export default Plot;
}

declare module 'plotly.js-dist-min';
