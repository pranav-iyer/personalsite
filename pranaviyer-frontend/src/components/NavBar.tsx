const NavBar = () => {
  return (
    <nav className="navbar navbar-expand-sm navbar-light border-bottom border-dark py-0 mb-2">
      <div className="container-fluid px-0">
        <a
          href={import.meta.env.VITE_API_BASE_URL}
          className="text-dark navbar-brand me-1 py-2"
        >
          Pranav Iyer
        </a>
        <button
          className="navbar-toggler border-0"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#pranav-iyer-nav"
          aria-controls="pranav-iyer-nav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              className="svg-icon"
              viewBox="0 0 16 16"
            >
              <path
                fillRule="evenodd"
                d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
              />
            </svg>
          </span>
        </button>
        <div className="collapse navbar-collapse" id="pranav-iyer-nav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <a
                className="nav-link py-0 text-dark"
                href={`${import.meta.env.VITE_API_BASE_URL}/about`}
              >
                About
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link py-0 text-dark"
                href={`${import.meta.env.VITE_API_BASE_URL}/blog`}
              >
                Blog
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link py-0 text-dark"
                href={`${import.meta.env.VITE_API_BASE_URL}/dash`}
              >
                Dash
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link py-0 text-dark"
                href={`${import.meta.env.VITE_API_BASE_URL}/admin`}
              >
                Admin
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link py-0 text-dark"
                href={`${import.meta.env.VITE_API_BASE_URL}/logout`}
              >
                Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
