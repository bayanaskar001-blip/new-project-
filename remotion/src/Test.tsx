import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
export const Test: React.FC = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f, fps});
  return (
    <AbsoluteFill style={{background: '#111', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{color: 'white', fontSize: 110, fontWeight: 800, fontFamily: 'sans-serif',
        transform: `scale(${s})`, opacity: interpolate(f, [0, 10], [0, 1])}}>Привет!</div>
    </AbsoluteFill>
  );
};
