import { CogIcon } from "@heroicons/react/20/solid";

const Spinner = () => {
	return (
		<div className="flex justify-center items-center">
			<CogIcon className="w-16 h-16 animate-spin" />
		</div>
	);
};

export default Spinner;
