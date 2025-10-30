import React from 'react';

const BadgeTop = () => {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-black/5 bg-black/5 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-black/70">
      <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
      ТОП
    </span>
  );
};

export default BadgeTop;
