declare module 'vanta/dist/vanta.fog.min' {
  const FOG: (opts: Record<string, unknown>) => { destroy: () => void };
  export default FOG;
}
