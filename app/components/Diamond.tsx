export default function Diamond({ pulsing = false }: { pulsing?: boolean }) {
  return (
    <span
      aria-hidden="true"
      className={`block w-[22px] h-[22px] shrink-0 bg-terracotta [clip-path:polygon(50%_0,100%_50%,50%_100%,0_50%)] ${
        pulsing ? 'animate-breathe' : ''
      }`}
    />
  );
}
